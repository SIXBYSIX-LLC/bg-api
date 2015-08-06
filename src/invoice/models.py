from django.db import models, transaction
from djangofuture.contrib.postgres import fields as pg_fields
from model_utils.managers import QueryManager

from common.models import BaseModel, DateTimeFieldMixin, BaseManager
from common import fields as ex_fields, errors
from . import messages
from transaction import constants as trans_const


class InvoiceManager(BaseManager):
    def create_from_order(self, order):
        with transaction.atomic():
            # Creating order
            invoice = self.model(order=order, user=order.user, is_approve=True,
                                 is_for_order=True)
            invoice.save()

            # Add purchase Item
            for item in order.purchaseitem_set.all():
                invoiceline = InvoiceLine.objects.get_or_create(
                    user_id=item.detail.get('user'), invoice=invoice, is_approve=True
                )[0]

                # Adding items to invoice
                description = "%s\nSKU: %s" % (item.detail.get('name'), item.detail.get('sku'))
                Item.objects.create(
                    invoice=invoice,
                    invoiceline=invoiceline,
                    qty=item.qty,
                    description=description,
                    user=item.orderline.user,
                    subtotal=item.subtotal,
                    shipping_charge=item.shipping_charge,
                    cost_breakup=item.cost_breakup,
                    unit_price=item.cost_breakup['subtotal'].get('unit_price'),
                    order_item=item
                )

            # Add rental items
            for item in order.rentalitem_set.all():
                invoiceline = InvoiceLine.objects.get_or_create(
                    user_id=item.detail.get('user'), invoice=invoice, is_approve=True
                )[0]

                description = "%s\nSKU: %s\nRent from %s to %s\nPost paid payment" % (
                    item.detail.get('name'), item.detail.get('sku'), item.date_start.isoformat(),
                    item.date_end.isoformat()
                )
                Item.objects.create(
                    invoice=invoice,
                    invoiceline=invoiceline,
                    qty=item.qty,
                    description=description,
                    user=item.orderline.user,
                    subtotal=0,
                    shipping_charge=0,
                    cost_breakup={'additional_charge': {}},
                    unit_price=0,
                    order_item=item,
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
    is_for_order = models.NullBooleanField(default=None)
    #: Is invoice approved by seller
    is_approve = models.BooleanField(default=False)

    objects = InvoiceManager()
    approved = QueryManager(is_approve=True)

    class Meta(BaseModel.Meta):
        unique_together = ('user', 'order', 'is_for_order')

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
        for item in Item.objects.filter(invoice=self):
            for k, v in item.cost_breakup['additional_charge'].items():
                if breakup.get(k, None) is None:
                    breakup[k] = 0.0
                breakup[k] += v

        return {'additional_charge': breakup}

    @transaction.atomic
    def mark_paid(self, force=False, confirm_order=True):
        """
        Mark this invoice as paid. By default it look for at least one transaction to succeeded
        for the invoice

        :param bool force: if False, it'll mark as paid without transaction check
        :param confirm_order: If True, it'll mark associate order as confirmed
        :return:
        :raise PaymentError: If no success transaction found for the invoice
        """
        if self.is_paid is True:
            return

        if force is False:
            # To mark as paid invoice.transaction_set should have at least 1 transaction success
            trans_ok_cnt = self.transaction_set.filter(status=trans_const.Status.SUCCESS).count()
            if trans_ok_cnt == 0:
                raise errors.PaymentError(*messages.ERR_TRANSACTION_CONFIRM)

        # Marking as paid
        self.is_paid = True
        self.save(update_fields=['is_paid'])

        # Marking order as confirm
        if confirm_order is True:
            self.order.confirm()


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

    @property
    def additional_charge(self):
        charge = 0.0

        for k, v in self.cost_breakup['additional_charge'].items():
            charge += v

        return charge

    def clean(self):
        # Raise an error if invoiceline is marked as approved by seller. which means once
        # approved seller is not allowed to edit it
        if self.invoiceline.is_approve is True:
            raise errors.InvoiceError(*messages.ERR_ITEM_EDIT)
