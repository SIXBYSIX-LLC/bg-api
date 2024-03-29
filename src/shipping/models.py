"""
======
Models
======
"""

from django.db import models

from common.models import BaseManager, BaseModel
from common import fields as ex_fields


class ShippingManager(BaseManager):
    def get_cost(self, cart):
        """
        Get shipping cost. This method should be overridden and calculate the shipping cost by
        looking into the cart products and delivery location

        :param Cart cart: Instance of cart

        :return Dict: Containing the shipping cost for each product
        """


class ShippingBase(BaseModel):
    """
    Base class for shipping methods
    """
    user = models.ForeignKey('miniauth.User')
    #: Source location
    origin = models.ForeignKey('usr.Address')

    name = 'Generic shipping'

    class Meta(BaseModel.Meta):
        abstract = True


class StandardMethod(ShippingBase):
    """
    Class to store rules for Standard shipping
    """
    #: County that rule belongs to
    country = models.ForeignKey('cities.Country')
    #: Zip code range or only zip code
    zipcode_start = models.PositiveIntegerField(db_index=True)
    zipcode_end = models.PositiveIntegerField(default=0, db_index=True)
    delivery_days = models.PositiveSmallIntegerField()
    # Shipping cost for the rule
    cost = ex_fields.FloatField(min_value=0, max_value=9999, precision=2)

    objects = ShippingManager()

    name = 'Standard shipping'
