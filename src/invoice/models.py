from django.db import models, transaction
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseModel, DateTimeFieldMixin, BaseManager
from common import fields as ex_fields, errors
from . import messages


class InvoiceManager(BaseManager):
    def create_from_order(self, order):
        with transaction.atomic():
            # Creating order
            invoice = self.model(order=order, user=order.user, is_approve=True,
                                 is_for_order=True)
            invoice.save()

            # Add Item
            for item in order.purchaseitem_set.all():
                invoiceline = InvoiceLine.objects.get_or_create(
                    user=item.orderline.user, invoice=invoice, is_approve=True
                )[0]


                # Adding items to invoice
                description = "%s\nSKU: %s" % (item.detail.get('name'), item.detail.get('sku'))
                item = Item.objects.create(
                    invoice=order,
                    invoiceline=invoiceline,
                    qty=item.qty,
                    description=description,
                    user=item.orderline.user,
                    subtotal=item.subtotal,
                    shipping_charge=item.shipping_charge,
                    additional_charge=item.additional_charge,
                    cost_breakup=item.cost_breakup,
                    unit_price=item.cost_breakup.get('unit_price'),
                )

        return invoice


class Invoice(BaseModel, DateTimeFieldMixin):
    #: Buyer
    user = models.ForeignKey('miniauth.User')
    #: Note mentioned while checkout (special instruction)
    order_note = models.TextField(null=True, default=None)
    #: Purchase order
    po = models.CharField(max_length=50, default='')
    #: Order which this invoice is related to
    order = models.ForeignKey('order.Order')
    #: Indicates if payment is done
    is_paid = models.BooleanField(default=False)
    #: Indicates if the invoice is for whole order or for rental items, also decides if the
    # invoice is editable or not
    is_for_order = models.BooleanField()
    #: Is invoice approved by seller
    is_approve = models.BooleanField(default=False)

    objects = InvoiceManager()

    class Meta(BaseModel.Meta):
        unique_together = ('user', 'is_for_order')

    @property
    def total(self):
        total = 0.0
        for item in Item.objects.filter(invoice=self):
            total += item.total

        return total

    @property
    def subtotal(self):
        subtotal = 0.0
        for item in Item.objects.filter(invoice=self):
            subtotal += item.subtotal

        return subtotal

    @property
    def shipping_charge(self):
        shipping = 0.0
        for item in Item.objects.filter(invoice=self):
            shipping += item.shipping

        return shipping

    @property
    def additional_charge(self):
        charge = 0.0
        for item in Item.objects.filter(invoice=self):
            charge += item.additional_charge

        return charge

    @property
    def cost_breakup(self):
        breakup = {}
        for item in Item.objects.filter(invoiceline=self):
            for k, v in item.cost_breakup['additional_charge'].items():
                if breakup.get(k, None) is None:
                    breakup[k] = 0.0
                breakup[k] += v

        return {'additional_charge': breakup}


class InvoiceLine(BaseModel):
    #: User as seller
    user = models.ForeignKey('miniauth.User')
    #: Invoice
    invoice = models.ForeignKey(Invoice)
    #: Indicates if seller has approved his part of the invoice or not. Once mark as approved
    is_approve = models.BooleanField(default=False)
    #: Just for seller's note, not visible to buyer
    remark = models.TextField(default='')

    @property
    def total(self):
        total = 0.0
        for item in Item.objects.filter(invoiceline=self):
            total += item.total

        return total

    @property
    def subtotal(self):
        subtotal = 0.0
        for item in Item.objects.filter(invoiceline=self):
            subtotal += item.subtotal

        return subtotal

    @property
    def shipping_charge(self):
        shipping = 0.0
        for item in Item.objects.filter(invoiceline=self):
            shipping += item.shipping

        return shipping

    @property
    def additional_charge(self):
        charge = 0.0
        for item in Item.objects.filter(invoiceline=self):
            charge += item.additional_charge

        return charge

    @property
    def cost_breakup(self):
        breakup = {}
        for item in Item.objects.filter(invoiceline=self):
            for k, v in item.cost_breakup['additional_charge'].items():
                if breakup.get(k, None) is None:
                    breakup[k] = 0.0
                breakup[k] += v

        return {'additional_charge': breakup}


class Item(BaseModel, DateTimeFieldMixin):
    #: Seller
    user = models.ForeignKey('miniauth.User', related_name='+')
    invoice = models.ForeignKey(Invoice)
    #: InvoiceLine is Group by seller user
    invoiceline = models.ForeignKey(InvoiceLine)
    #: Order item which this item related to
    order_item = models.ForeignKey('order.Item', related_name='invoice_item')
    #: Item description. Computer generated description would contain the item name,
    #: rental period, and other information
    description = models.CharField(max_length=500)
    #: Quantity
    qty = models.PositiveSmallIntegerField()
    #: Unit price, it's not applicable for rental item
    unit_price = ex_fields.FloatField(min_value=0.0, precision=2)
    #: Sub total
    subtotal = ex_fields.FloatField(min_value=0.0, precision=2)
    #: Shipping charge
    shipping_charge = ex_fields.FloatField(min_value=0.0, precision=2)
    #: Additional charge including sales tax
    additional_charge = ex_fields.FloatField(min_value=0.0, precision=2)
    #: Overuse charge, it should include difference of sales tax and any other charges
    overuse_charge = ex_fields.FloatField(min_value=0.0, precision=2, default=0)
    #: Cost break up of subtotal / shipping charge and additional charge
    cost_breakup = pg_fields.JSONField(default={})
    #: For rental item, Date from
    date_from = models.DateTimeField(default=None, null=True)
    #: For rental item, Date to
    date_to = models.DateTimeField(default=None, null=True)

    @property
    def total(self):
        return round(self.subtotal + self.shipping_charge + self.additional_charge +
                     self.overuse_charge, 2)

    def clean(self):
        # Raise an error if invoiceline is marked as approved by seller. which means once
        # approved seller is not allowed to edit it
        if self.invoiceline.is_approve is True:
            raise errors.InvoiceError(*messages.ERR_ITEM_EDIT)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Item, self).save(*args, **kwargs)
