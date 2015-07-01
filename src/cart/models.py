import logging

from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseManager, BaseModel, DateTimeFieldMixin
from . import constants

L = logging.getLogger('bgapi.' + __name__)


class CartManager(BaseManager):
    pass


class Cart(BaseModel, DateTimeFieldMixin):
    SHIPPING_KIND = (
        (constants.SHIPPING_PICKUP, 'Pickup'),
        (constants.SHIPPING_DELIVERY, 'Delivery'),
    )

    rental_products = models.ManyToManyField('catalog.Product', through='RentalItem')
    #: Shipping Location
    location = models.ForeignKey('usr.Address', null=True, default=None)
    #: How shipping will be made?
    shipping_kind = models.CharField(max_length=20, choices=SHIPPING_KIND, null=True, default=None)
    #: Cart owner
    user = models.ForeignKey('miniauth.User', blank=True, editable=False)
    #: This value can be false in case it's converted to order or by other conditions in future
    is_active = models.BooleanField(default=True, editable=False)
    #: Total estimated cost to be paid
    total = pg_fields.JSONField(editable=False, default={})

    Const = constants

    class Meta(BaseModel.Meta):
        db_table = 'cart'


class Item(BaseModel):
    cart = models.ForeignKey('Cart')
    product = models.ForeignKey('catalog.Product')
    # Shipping cost
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Item quantity
    qty = models.PositiveSmallIntegerField(default=1)

    class Meta(BaseModel.Meta):
        abstract = True


class RentalItem(Item):
    # Item to be delivered by
    date_start = models.DateTimeField()
    # Item to be returned
    date_end = models.DateTimeField()

    class Meta(Item.Meta):
        unique_together = ('cart', 'product', 'date_start', 'date_end')
