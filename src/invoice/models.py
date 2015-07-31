from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseModel, DateTimeFieldMixin
from common import fields as ex_fields


class Invoice(BaseModel, DateTimeFieldMixin):
    #: Seller
    user = models.ForeignKey('miniauth.User')
    #: Client / Buyer
    to_user = models.ForeignKey('miniauth.User', related_name='+')
    #: forms of trade credit which specify that the net amount is expected to be paid in full
    #: and received by specified days
    net_term = models.PositiveSmallIntegerField()
    #: Note to client
    note = models.TextField(null=True, default=None)
    #: Note mentioned while checkout (special instruction)
    order_note = models.TextField(null=True, default=None)
    #: Purchase order
    po = models.CharField(max_length=50, default='')
    #: Discount value
    discount_value = ex_fields.FloatField(min_value=0.1, max_value=999999999, precision=2)
    #: Discount kind
    discount_kind = models.CharField(max_length=20, default=None, null=True)
    #: Order which this invoice is related to
    order = models.ForeignKey('order.Order')
    #: Indicates if payment is done
    is_paid = models.BooleanField(default=False)
    #: Total is dict that contains subtotal, taxes, any additional charges and total amount to be
    #:  paid (after applying the discount)
    total = pg_fields.JSONField(default={})
    due_date = models.DateField()


class Item(BaseModel, DateTimeFieldMixin):
    invoice = models.ForeignKey(Invoice)
    #: Order item which this item related to
    journal = models.ForeignKey('transaction.Journal', related_name='invoice_item')
    #: Item description. Computer generated description would contain the item name,
    #: rental period, and other information
    description = models.CharField(max_length=500)
    #: Quantity
    qty = models.PositiveSmallIntegerField(default=1)
    unit_price = ex_fields.FloatField(min_value=0.0, max_length=99999999, precision=2)

    @property
    def total(self):
        return round(self.unit_price * self.quantity, 2)
