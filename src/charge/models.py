from django.db import models
from django.db.models import Q

from common.models import BaseModel, BaseManager
from common import fields as ex_fields
from . import constants


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


class Rental(object):
    def __init__(self, start_date, end_date, item):
        self.user = item.user
        self.start_date, self.end_date, self.item = start_date, end_date, item

    def calculate(self):
        settings = self.item.user.profile.settings
        unit = self.applicable_units(
            settings.get('hourly_price_till_hours', 4), settings.get('daily_price_till_days', 3),
            settings.get('weekly_price_till_days', 15), self.end_date, self.start_date
        )

        price = {'daily': self.item.daily_price, 'weekly': self.item.weekly_price,
                 'monthly': self.item.monthly_price, 'hourly': self.item.hourly_price}

        subtotal = {'hourly': price['hourly'] * unit['final']['hours'],
                    'daily': price['daily'] * unit['final']['days'],
                    'weekly': price['weekly'] * unit['final']['weeks'],
                    'monthly': price['monthly'] * unit['final']['months']}

        amt = 0.0
        for v in subtotal.items():
            amt += v

        amt = round(amt, 2)
        data = {'unit': unit, 'prices': price, 'subtotal': subtotal, 'amt': amt}
        return data

    @classmethod
    def applicable_units(cls, start_date, end_date, hourly_slab, daily_slab, weekly_slab):
        data = {}
        calc = {}
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
