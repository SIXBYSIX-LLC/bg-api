import logging

from django.db import models
from django.db.models import Q
from django.utils.text import slugify

from common.models import BaseModel, BaseManager
from common import fields as ex_fields
from . import constants
from shipping import constants as ship_const


L = logging.getLogger('bgapi.' + __name__)


class Charge(BaseModel):
    UNITS = (
        (constants.Unit.PERCENTAGE, 'Percentage'),
        (constants.Unit.FLAT, 'Flat'),
    )
    name = models.CharField(max_length=50, default='Tax')
    value = ex_fields.FloatField(min_value=0, max_value=9999, precision=2)
    unit = models.CharField(choices=UNITS, max_length=30)

    class Meta(BaseModel.Meta):
        abstract = True


class SalesTax(Charge):
    country = models.ForeignKey('cities.Country')
    state = models.ForeignKey('cities.Region', null=True)

    class Meta(Charge.Meta):
        unique_together = ('country', 'state')


class AdditionalChargeManager(BaseManager):
    def all_by_natural_key(self, user, item_kind, category):
        hierarchy = category.hierarchy + [category.id]

        # Get charges that applies on all item and categories
        q_all = Q(item_kind='all', categories__isnull=True)

        # Get charges that applies only on item_kind
        q_kind = Q(item_kind=item_kind, categories__isnull=True)

        # Get charges that applies on all item and only specific category
        q_cat = Q(item_kind='all', categories__id__in=hierarchy)

        # Get charges for the specific item kind and category
        q_specific = Q(item_kind=item_kind, categories__id__in=hierarchy)

        return self.filter(q_all | q_kind | q_cat | q_specific, user=user)


class AdditionalCharge(Charge):
    """
    This charge is the addition/extra charges that user can define. For eg, environment fee, vat

    This can be configured either for rental or purchase item and various categories only
    """

    ITEM_KIND = (
        (constants.ItemKind.PURCHASE, 'Purchase'),
        (constants.ItemKind.RENTAL, 'Rental'),
        (constants.ItemKind.ALL, 'All'),
    )
    #: Either applicable on rental or purchase or all
    item_kind = models.CharField(choices=ITEM_KIND, max_length=30)
    #: User can specify the category on which
    categories = models.ManyToManyField('category.Category')
    #: Owner
    user = models.ForeignKey('miniauth.User', default=None)

    objects = AdditionalChargeManager()

    Const = constants

    class Meta(Charge.Meta):
        unique_together = ('name', 'user')


class Calculator(object):
    def __init__(self, product, qty):
        self.product, self.qty = product, qty

    def calc_rent(self, start_date, end_date):
        settings = self.product.user.profile.settings
        rent_period = self.effective_rent_period(
            start_date, end_date,
            settings.get('hourly_price_till_hours', 4), settings.get('daily_price_till_days', 3),
            settings.get('weekly_price_till_days', 15)
        )

        price = {'daily': self.product.daily_price, 'weekly': self.product.weekly_price,
                 'monthly': self.product.monthly_price, 'hourly': self.product.hourly_price}

        subtotal = {'hourly': price['hourly'] * rent_period['final']['hours'],
                    'daily': price['daily'] * rent_period['final']['days'],
                    'weekly': price['weekly'] * rent_period['final']['weeks'],
                    'monthly': price['monthly'] * rent_period['final']['months']}

        amt = 0.0
        for v in subtotal.values():
            amt += v

        unit_price = round(amt, 2)
        amt = unit_price * self.qty
        data = {'rent_period': rent_period, 'prices': price, 'subtotal': subtotal, 'amt': amt,
                'unit_price': unit_price}
        return data

    def calc_additional_charge(self, base_amount, item_kind, marge_other_charge={}):
        """
        Calculates any additional charges levied by seller and sales tax

        :return dict:
        """
        data = {'amt': 0.0}
        charge_const = AdditionalCharge.Const
        charges = AdditionalCharge.objects.all_by_natural_key(
            self.product.user, item_kind, self.product.category
        )

        for charge in charges:
            k = slugify(charge.name).replace('-', '_')
            if charge.unit == charge_const.Unit.FLAT:
                data[k] = charge.value
                data['amt'] += charge.value * self.qty
            elif charge.unit == charge_const.Unit.PERCENTAGE:
                value = round((base_amount * charge.value) / 100, 2)
                data[k] = value
                data['amt'] += value * self.qty

        data.update(**marge_other_charge)
        # Add other charges amount to total amount
        for k, v in marge_other_charge.items():
            data['amt'] += v

        return data

    def calc_shipping_charge(self, shipping_address, shipping_kind):
        shipping_method = self.product.get_standard_shipping_method(shipping_address)

        data = {'amt': 0.0}

        if shipping_kind == ship_const.SHIPPING_PICKUP:
            L.info('Shipping cost', extra=data)
            return data
        if not shipping_method:
            L.info('Item is not shippable', extra={'product': self.product.id})
            return data

        # Shipping standard method
        data['amt'] = round(shipping_method.cost * self.qty, 2)
        data['method'] = 'standard_shipping'
        data['id'] = shipping_method.id

        L.info('Shipping cost', extra=data)

        return data

    @classmethod
    def calc_sales_tax(cls, amt, sales_tax):
        tax = {'pct': 0, 'amt': 0.0}

        if sales_tax:
            tax['taxable_amt'] = amt
            tax['id'] = sales_tax.id
            tax['pct'] = sales_tax.value
            tax['amt'] = round((amt * sales_tax.value) / 100, 2)

        return tax

    @classmethod
    def get_sales_tax(cls, country, state):
        """
        :return: Get sales tax percentage
        """
        try:
            tax = SalesTax.objects.get(country=country, state=state)
        except SalesTax.DoesNotExist:
            return None
        except AttributeError:
            return None
        else:
            return tax

    @classmethod
    def effective_rent_period(cls, start_date, end_date, hourly_slab, daily_slab, weekly_slab):
        daily_slab *= 8
        weekly_slab *= 8

        daily_hours = 1 * 8
        weekly_hours = 7 * daily_hours
        monthly_hours = 28 * daily_hours

        td = end_date - start_date
        days = td.days
        hours = td.seconds / 3600
        minutes = (td.seconds / 60) % 60
        # If minutes is more than 5, count it as an hour
        if minutes > 5:
            hours += 1

        total_hours = (days * 8) + hours
        data = {'actual': str(td), 'adjusted': '%s days, %s:00:00' % (days, hours)}

        rent_hours = rent_days = rent_weeks = rent_months = 0

        rent_months = total_hours / monthly_hours
        rent_month_diff_hrs = total_hours % monthly_hours

        if rent_month_diff_hrs > weekly_slab:
            rent_months += 1
        else:
            rent_weeks = rent_month_diff_hrs / weekly_hours
            rent_week_diff_hrs = rent_month_diff_hrs % weekly_hours

            if rent_week_diff_hrs > daily_slab:
                rent_weeks += 1
            else:
                rent_days = rent_week_diff_hrs / daily_hours
                rent_days_diff_hrs = rent_week_diff_hrs % daily_hours

                if rent_days_diff_hrs > hourly_slab:
                    rent_days += 1
                else:
                    rent_hours = rent_days_diff_hrs

        data['final'] = {
            'months': rent_months, 'weeks': rent_weeks, 'days': rent_days, 'hours': rent_hours
        }
        return data
