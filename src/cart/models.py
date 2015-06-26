from django.db import models

from common.models import BaseManager, BaseModel, DateTimeFieldMixin
from . import constants


class CartManager(BaseManager):
    pass


class Cart(BaseModel, DateTimeFieldMixin):
    SHIPPING_KIND = (
        (constants.SHIPPING_PICKUP, 'Pickup'),
        (constants.SHIPPING_DELIVERY, 'Delivery'),
    )

    products = models.ManyToManyField('catalog.Product', through='Item')
    #: Shipping Location
    location = models.ForeignKey('usr.Address', null=True, default=None)
    #: How shipping will be made?
    shipping_kind = models.CharField(max_length=20, choices=SHIPPING_KIND, null=True, default=None)
    #: Cart owner
    user = models.ForeignKey('miniauth.User', blank=True, editable=False)

    Const = constants

    class Meta(BaseModel.Meta):
        db_table = 'cart'


class Item(BaseModel):
    cart = models.ForeignKey('Cart')
    product = models.ForeignKey('catalog.Product')
    # Item to be delivered by
    date_start = models.DateTimeField(null=True, default=None)
    # Item to be returned
    date_end = models.DateTimeField(null=True, default=None)
    # Shipping cost
    shipping_price = models.DecimalField(max_length=10, decimal_places=2)
    subtotal = models.DecimalField(max_length=10, decimal_places=2)
    # Item quantity
    qty = models.PositiveSmallIntegerField()
