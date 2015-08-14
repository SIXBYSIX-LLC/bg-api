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
        price = {
            'daily_price': self.product.daily_price, 'weekly_price': self.product.weekly_price,
            'monthly_price': self.product.monthly_price, 'hourly_price': self.product.hourly_price
        }
        rent_period = self.effective_rent_period(start_date, end_date, **price)

        subtotal = {
            'hourly': price['hourly_price'] * rent_period['final']['hours'],
            'daily': price['daily_price'] * rent_period['final']['days'],
            'weekly': price['weekly_price'] * rent_period['final']['weeks'],
            'monthly': price['monthly_price'] * rent_period['final']['months'],
        }

        amt = 0.0
        for v in subtotal.values():
            amt += v

        unit_price = round(amt, 2)
        amt = unit_price * self.qty
        data = {'rent_period': rent_period, 'prices': price, 'subtotal': subtotal, 'amt': amt,
                'unit_price': unit_price}
        return data

    def calc_additional_charge(self, base_amount, item_kind, *marge_other_charge):
        """
        Calculates any additional charges levied by seller and sales tax

        :param list marge_other_charge:
            The charge object should be the dict and contain the `amt` and `name`
        :return dict:
        """
        from serializers import AdditionalChargeSerializer

        amt = 0.0
        data = []
        charge_const = AdditionalCharge.Const
        charges = AdditionalCharge.objects.all_by_natural_key(
            self.product.user, item_kind, self.product.category
        )

        for charge in charges:
            c = AdditionalChargeSerializer(charge).data
            if charge.unit == charge_const.Unit.FLAT:
                c['amt'] = charge.value * self.qty
                amt += charge.value * self.qty
            elif charge.unit == charge_const.Unit.PERCENTAGE:
                value = round((base_amount * charge.value) / 100, 2)
                c['amt'] = value * self.qty
                amt += value * self.qty
            data.append(c)

        data.extend(marge_other_charge)

        # Add other charges amount to total amount
        for charge in marge_other_charge:
            amt += charge['amt']

        return amt, data

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
    def calc_items_total(cls, items):
        """
        Calculates total of the items. Item should be th object of cart.Item or order.Item

        :param list items: List of cart.Item or order.Item
        :return dict:
            {
                'shipping_charge': float,
                'subtotal': float,
                'additional_charge': float,
                'cost_breakup': {
                    'additional_charge': BREAKUP_OF_ADDTIONAL_CHARGES
                }
            }
        """
        shipping_charge = 0
        subtotal = 0
        ad_charge_amt = 0
        ad_charge_breakup = {}

        for item in items:
            shipping_charge += item.shipping_charge
            subtotal += item.subtotal
            ad_charge_amt += item.additional_charge

            for charge in item.cost_breakup['additional_charge']:
                k = slugify(charge.get('name')).replace('-', '_')
                v = charge.get('amt')
                # Initialize value
                if ad_charge_breakup.get(k, None) is None:
                    ad_charge_breakup[k] = 0.0
                ad_charge_breakup[k] += v

        return {
            'shipping_charge': shipping_charge,
            'subtotal': subtotal,
            'additional_charge': ad_charge_amt,
            'cost_breakup': {
                'additional_charge': ad_charge_breakup
            }
        }


    @classmethod
    def calc_sales_tax(cls, amt, sales_tax):
        tax = {'pct': 0, 'amt': 0.0, 'name': 'Sales tax'}

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
    def effective_rent_period(cls, start_date, end_date, **kwargs):
        """
        This function needs cleanup and should simplified

        :param start_date:
        :param end_date:
        :param kwargs:
        :return:
        """
        hourly_price = kwargs.get('hourly_price')
        daily_price = kwargs.get('daily_price')
        weekly_price = kwargs.get('weekly_price')
        monthly_price = kwargs.get('monthly_price')

        td = end_date - start_date
        days = td.days
        hours = td.seconds / 3600
        minutes = (td.seconds / 60) % 60
        # If minutes is more than 5, count it as an hour
        if minutes > 5:
            hours += 1

        total_hours = days * 8 + hours
        data = {'actual': str(td), 'adjusted': '%s days, %s:00:00' % (days, hours)}

        # Calculate rent if counted as hours for given period
        # Dict to hold final effective period
        hourly_effective_period = {'months': 0, 'weeks': 0, 'days': 0, 'hours': total_hours}
        rent_as_hours = total_hours * hourly_price

        # Calculate rent if counted as days and carry hours for given period
        daily_effective_period = {'months': 0, 'weeks': 0, 'days': days, 'hours': hours}
        carry_hours_rent_or_daily = carry_hours_rent = hours * hourly_price
        # Decides which rent is more cheaper if counted as hours(hours) or as a day
        if carry_hours_rent > daily_price:
            daily_effective_period.update({'days': days + 1, 'hours': 0})
            carry_hours_rent_or_daily = daily_price
        rent_as_days = days * daily_price + carry_hours_rent_or_daily

        # Calculate rent if counted as weeks and carry days and carry hours for given period
        def calc_for_weeks(d, hours_rent_or_daily):
            weeks = d / 7
            weekly_period = {'months': 0, 'weeks': weeks, 'days': 0, 'hours': 0}
            if weeks is 0:
                rent = d * daily_price + carry_hours_rent_or_daily
                # Get hours or a day
                if carry_hours_rent_or_daily == daily_price:
                    weekly_period.update({'weeks': 0, 'days': d + 1, 'hours': 0})
                else:
                    weekly_period.update({'weeks': 0, 'days': d, 'hours': hours})
                if rent > weekly_price:
                    rent = weekly_price
                    weekly_period.update({'weeks': 1, 'days': 0, 'hours': 0})
                return rent, weekly_period

            # Count rent for carry days
            week_carry_days = days % 7
            # Decides if carry days rent is higher or weekly price
            if week_carry_days * daily_price > weekly_price:
                weekly_rent_or_daily = weekly_price
                weekly_period.update({'weeks': weeks + 1})
            else:
                # Calculate carry days rent including carry hours
                weekly_rent_or_daily = week_carry_days * daily_price + hours_rent_or_daily
                weekly_period.update({'days': week_carry_days, 'hours': hours})
                # If we found carry days + carry hours is higher than weekly_price, we'll swap it
                if weekly_rent_or_daily > weekly_price:
                    weekly_rent_or_daily = weekly_price
                    weekly_period.update({'days': week_carry_days + 1, 'hours': 0})

            return weeks * weekly_price + weekly_rent_or_daily, weekly_period

        rent_as_weeks, weekly_effective_period = calc_for_weeks(days, carry_hours_rent_or_daily)

        # Calculate as month
        months = days / 28
        monthly_effective_period = {'months': months, 'weeks': 0, 'days': 0, 'hours': 0}
        if months == 0:
            monthly_rent = monthly_price + carry_hours_rent_or_daily
            if carry_hours_rent_or_daily == daily_price:
                monthly_effective_period.update({'months': 1, 'weeks': 0, 'days': 1, 'hours': 0})
            else:
                monthly_effective_period.update(
                    {'months': 1, 'weeks': 0, 'days': 0, 'hours': hours})
        else:
            month_carry_days = days % 28

            # Count carry days rent as weeks
            weekly_carry_rent, w_period = calc_for_weeks(month_carry_days,
                                                         carry_hours_rent_or_daily)

            w_period.update({'months': months})
            if weekly_carry_rent > monthly_price:
                monthly_effective_period.update({'months': months + 1})
                weekly_rent_or_monthly = monthly_price
            else:
                monthly_effective_period.update(**w_period)
                weekly_rent_or_monthly = weekly_carry_rent

            monthly_rent = months * monthly_price + weekly_rent_or_monthly

        period_rents = {
            'hourly': rent_as_hours, 'daily': rent_as_days,
            'weekly': rent_as_weeks, 'monthly': monthly_rent
        }
        periods = {
            'hourly': hourly_effective_period, 'daily': daily_effective_period,
            'weekly': weekly_effective_period, 'monthly': monthly_effective_period
        }

        cheapest = ['hourly', period_rents['hourly']]
        for k, v in period_rents.items():
            if cheapest[1] > v:
                cheapest[1] = v
                cheapest[0] = k

        # print period_rents, periods
        # for period in periods.values():
        # total = 0
        # for k, v in period.items():
        # if k == 'hours':
        # total += v * hourly_price
        # elif k == 'days':
        #             total += v * daily_price
        #         elif k == 'weeks':
        #             total += v * weekly_price
        #         else:
        #             total += v * monthly_price
        #     print total

        data['final'] = periods[cheapest[0]]
        return data
