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

    class Meta(Charge.Meta):
        unique_together = ('name', 'user')
