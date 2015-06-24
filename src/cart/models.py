from django.db import models

from common.models import BaseManager, BaseModel


class CartManager(BaseManager):
    pass


class Cart(BaseModel):
    products = models.ManyToManyField('catalog.Product')
    #: Shipping Location
    location = models.ForeignKey('usr.Address', null=True, default=None)
    #: Date time when the cart is created
    date_created_at = models.DateTimeField(auto_now_add=True, blank=True, editable=False)
    #: Date time of cart updates
    date_updated_at = models.DateTimeField(auto_now=True, blank=True, editable=False)

    shipping_kind = models.CharField(max_length=20, choices=SHIPPING_KIND)
    # Cart of user
    user = models.ForeignKey('miniauth.User', blank=True, default=None, editable=False)


class Item(BaseModel):
    SHIPPING_KIND = (
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    )
    cart = models.ForeignKey('Cart')
    product = models.ForeignKey('catalog.Product')
    date_start = models.DateTimeField(null=True, default=None)
    date_end = models.DateTimeField(null=True, default=None)

    subtotal = models.DecimalField(max_length=10, decimal_places=2)
    # Item quantity
    qty = models.PositiveSmallIntegerField()
