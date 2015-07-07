from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseModel, DateTimeFieldMixin


class Order(BaseModel, DateTimeFieldMixin):
    # Cart, just for reference
    cart = models.ForeignKey('cart.Cart')
    # The user, who is creating the order
    user = models.ForeignKey('miniauth.User')
    # Address, copied from cart
    address = models.TextField()
    country = models.ForeignKey('cities.Country')
    state = models.ForeignKey('cities.Region')
    city = models.ForeignKey('cities.City')
    zip_code = models.CharField(max_length=15)

    class Meta(BaseModel.Meta):
        db_table = 'order'


class RentalItem(BaseModel):
    STATUS = (
        ('requested', 'Requested'),
        ('approved', 'Requested'),
        ('prepared', 'Requested'),
        ('dispatched', 'Requested'),
        ('shipped', 'Requested'),
    )
    #: Reference to order
    order = models.ForeignKey(Order)
    #: The user who is going to fulfill the item
    to_user = models.ForeignKey('miniauth.User')
    #: Inventory that is assigned to the item
    inventory = models.ForeignKey('catalog.Inventory', null=True, default=None)
    #: Product detail, copied from cart rental item
    detail = pg_fields.JSONField()
    #: The rental item status order
    is_approved = models.CharField()
    is_prepared = models.CharField()
    is_dispatched = models.CharField()
    #: Rental period
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    #: Subtotal including tax
    subtotal = models.FloatField()
    #: Subtotal breakup
    cost_breakup = pg_fields.JSONField()
    #: Quantity
    qty = models.PositiveSmallIntegerField()
    #:
    shipping_method = models.CharField(max_length=20)
    #:
    payment_method = models.CharField(max_length=20, default='postpaid')
