import logging

from django.db import models, transaction
from django.db.models import Q, Max
from django.utils import timezone
from djangofuture.contrib.postgres import fields as pg_fields
from model_utils.managers import QueryManager

from common.helper import round_off
from common.models import BaseModel, DateTimeFieldMixin, BaseManager
from common import fields as ex_fields, errors
from . import messages
from transaction import constants as trans_const
from order.models import RentalItem
from order import constants as ordr_const
from charge.models import Calculator

L = logging.getLogger('bgapi.' + __name__)


class InvoiceManager(BaseManager):
    @transaction.atomic()
    def create_from_order(self, order):
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
                date_from=item.date_start,
                date_to=item.date_start
            )

        return invoice

    @transaction.atomic()
    def generate_rental_invoices(self, num_days):
        # Creating order
        invoices = {}

        # For regular start date and end date contract
        qs = RentalItem.objects.filter(~Q(invoiceitem_set__is_final_invoice=True))
        qs = qs.annotate(last_invoiced_date=Max('invoiceitem_set__date_to'))
        qs = qs.annotate(invoiced_shipping_charge=Max('invoiceitem_set__shipping_charge'))
        qs = qs.filter(
            Q(last_invoiced_date__lte=timezone.now() - timezone.timedelta(days=num_days),
              statuses__status__in=[ordr_const.Status.DELIVERED, ordr_const.Status.PICKED_UP]) |
            Q(statuses__status=ordr_const.Status.END_CONTRACT)
        )

        for item in qs.all():
            order = item.order
            buyer = item.user
            seller_id = item.detail.get('user')
            invoice = invoices.get(order.id)

            if invoice is None:
                invoice = Invoice.objects.create(order=order, user=buyer, is_approve=False)
                invoices[order.id] = invoice

            # Creating or getting invoiceline
            invoiceline = InvoiceLine.objects.get_or_create(user_id=seller_id, invoice=invoice)[0]

            invoice_item = Item(
                user_id=seller_id,
                invoice=invoice,
                invoiceline=invoiceline,
                order_item=item,
                qty=item.qty,
                unit_price=item.cost_breakup['subtotal'].get('unit_price'),
                date_from=item.last_invoiced_date,
                date_to=item.last_invoiced_date + timezone.timedelta(days=num_days),
                is_final_invoice=False,
            )

            # If status is contract ended, change end date to contract end date
            if item.current_status.status == ordr_const.Status.END_CONTRACT:
                invoice_item.date_to = item.current_status.date_created_at
                invoice_item.is_final_invoice = True

            invoice_item.description = "%s\nSKU: %s\nRent from %s to %s" % (
                item.detail.get('name'), item.detail.get('sku'), invoice_item.date_from.isoformat(),
                invoice_item.date_to.isoformat()
            )

            invoice_item.calculate_cost(order, item.invoiced_shipping_charge, save=False)
            invoice_item.save()
            invoice_item.refresh_from_db()

        return invoices.values()

    def unapproved_for_days(self, days):
        return self.filter(
            is_approve=False, date_created_at__lte=timezone.now() - timezone.timedelta(days=days)
        )


class Invoice(BaseModel, DateTimeFieldMixin):
    """
    (Can not be deleted)
    """
    #: Buyer
    user = models.ForeignKey('miniauth.User')
    #: Note mentioned while checkout (special instruction)
    order_note = models.TextField(null=True, default=None)
    #: Purchase order
    po = models.CharField(max_length=50, default='')
    #: Order which this invoice is related to
    order = models.ForeignKey('order.Order')
    #: Indicates if payment is done
    is_paid = models.BooleanField(default=False, db_index=True)
    #: Indicates if the invoice is for whole order or for rental items, also decides if the
    # invoice is editable or not, it's kept null as to support unique index with other field
    is_for_order = models.NullBooleanField(default=None, db_index=True)
    #: Is invoice approved by seller
    is_approve = models.BooleanField(default=False, db_index=True)

    objects = InvoiceManager()
    approved = QueryManager(is_approve=True)

    class Meta(BaseModel.Meta):
        unique_together = ('user', 'order', 'is_for_order')
        permissions = (
            ('action_pay', 'Can pay invoice'),
        )

    @property
    def total(self):
        total = 0.0
        for item in Item.objects.filter(invoice=self):
            total += item.total

        return round_off(total)

    @property
    def subtotal(self):
        subtotal = 0.0
        for item in Item.objects.filter(invoice=self):
            subtotal += item.subtotal

        return round_off(subtotal)

    @property
    def shipping_charge(self):
        shipping = 0.0
        for item in Item.objects.filter(invoice=self):
            shipping += item.shipping

        return round_off(shipping)

    @property
    def additional_charge(self):
        charge = 0.0
        for item in Item.objects.filter(invoice=self):
            charge += item.additional_charge

        return round_off(charge)

    @property
    def cost_breakup(self):
        result = Calculator.calc_items_total(Item.objects.filter(invoice=self))

        return result.get('cost_breakup')

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

    @transaction.atomic
    def approve(self, force=False):
        L.debug('Approving invoice', extra={'force': force})

        unapproved_cnt = InvoiceLine.objects.filter(invoice=self, is_approve=False).count()
        if force is False:
            if unapproved_cnt > 0:
                raise errors.InvoiceError(*messages.ERR_APPROVE_INVOICE)
        elif force is True and unapproved_cnt > 0:
            InvoiceLine.objects.filter(invoice=self, is_approve=False).update(is_approve=True)

        self.is_approve = True
        self.save(update_fields=['is_approve'])


class InvoiceLine(BaseModel):
    """
    (Can not be deleted)
    """
    #: User as seller
    user = models.ForeignKey('miniauth.User')
    #: Invoice
    invoice = models.ForeignKey(Invoice)
    #: Indicates if seller has approved his part of the invoice or not. Once mark as approved
    is_approve = models.BooleanField(default=False, db_index=True)
    #: Just for seller's note, not visible to buyer
    remark = models.TextField(default='')

    class Meta(BaseModel.Meta):
        permissions = (
            ('action_approve', 'Can approve invoiceline'),
        )

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

    def approve(self):
        self.is_approve = True
        self.save(update_fields=['is_approve'])

        try:
            self.invoice.approve()
        except errors.InvoiceError:
            pass


class Item(BaseModel, DateTimeFieldMixin):
    """
    (Can not be deleted)
    """
    #: Seller
    user = models.ForeignKey('miniauth.User', related_name='+')
    invoice = models.ForeignKey(Invoice)
    #: InvoiceLine is Group by seller user
    invoiceline = models.ForeignKey(InvoiceLine)
    #: Order item which this item related to
    order_item = models.ForeignKey('order.Item', related_name='invoiceitem_set')
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
    date_from = models.DateTimeField(default=None, null=True, db_index=True)
    #: For rental item, Date to
    date_to = models.DateTimeField(default=None, null=True, db_index=True)
    #: Indicates if this item contract is ended and invoiced last time
    is_final_invoice = models.BooleanField(default=False, db_index=True)

    @property
    def total(self):
        return self.subtotal + self.shipping_charge + self.additional_charge + self.overuse_charge

    @property
    def additional_charge(self):
        charge = 0.0

        for ad_charge in self.cost_breakup['additional_charge']:
            charge += ad_charge['amt']

        return charge

    def clean(self):
        # Raise an error if invoiceline is marked as approved by seller. which means once
        # approved seller is not allowed to edit it
        if self.invoiceline.is_approve is True:
            raise errors.InvoiceError(*messages.ERR_ITEM_EDIT)

    def calculate_cost(self, order, invoiced_shipping_charge, save=True):
        calc = Calculator(self.order_item.product, self.qty)
        subtotal_breakup = calc.calc_rent(self.date_from, self.date_to)
        subtotal = subtotal_breakup['amt']

        # Copy shipping charges from order
        shipping = 0
        shipping_breakup = {'amt': 0}
        if invoiced_shipping_charge == 0:
            shipping_breakup = self.order_item.cost_breakup.get('shipping')
            shipping = shipping_breakup['amt']

        st = calc.get_sales_tax(order.shipping_address)
        sales_tax = calc.calc_sales_tax(subtotal + shipping, st)

        additional_charge = self._calculate_additional_charge(subtotal, sales_tax)

        cost_breakup = {'subtotal': subtotal_breakup, 'additional_charge': additional_charge,
                        'shippping': shipping_breakup, 'sales_tax': sales_tax}

        self.subtotal = subtotal
        self.shipping_charge = shipping
        self.cost_breakup = cost_breakup

        if save is True:
            self.save(update_fields=['subtotal', 'shipping_charge', 'cost_breakup'])

    def _calculate_additional_charge(self, base_amount, *other_charges):
        data = []

        for charge in self.order_item.cost_breakup['additional_charge']:
            # Ignore the merged charges as it needs to be calculated separately and usually
            # provided with other_charges args
            if charge.get('merged') is True:
                continue

            data.append(charge)
            charge['amt'] = Calculator._calculate_pct_flat(base_amount, charge.get('unit'),
                                                           charge.get('value'), self.qty)

        for ch in other_charges:
            ch['merged'] = True
        data.extend(other_charges)

        return data
