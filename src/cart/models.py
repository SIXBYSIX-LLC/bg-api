import logging

from django.db import models, transaction
from djangofuture.contrib.postgres import fields as pg_fields

from cart.validators import validate_date_start
from common.models import BaseManager, BaseModel, DateTimeFieldMixin
from common import fields as ex_fields, errors
from charge.models import SalesTax, AdditionalCharge, Calculator
from . import constants, messages
from shipping import constants as ship_const
from order.models import Order
from invoice.models import Invoice

L = logging.getLogger('bgapi.' + __name__)


class CartManager(BaseManager):
    pass


class Cart(BaseModel, DateTimeFieldMixin):
    #: Shipping Location
    location = models.ForeignKey('usr.Address', null=True, default=None)
    #: Billing address
    billing_address = models.ForeignKey('usr.Address', null=True, default=None, related_name='+')
    #: Cart owner
    user = models.ForeignKey('miniauth.User', blank=True, editable=False)
    #: This value can be false in case it's converted to order or by other conditions in future
    is_active = models.BooleanField(default=True, editable=False)
    #: Subtotal
    subtotal = models.FloatField(editable=False, default=0)
    #: Shipping charge
    shipping_charge = models.FloatField(editable=False, default=0)
    #: Additional charges
    additional_charge = models.FloatField(editable=False, default=0)
    #: Cost breakups
    cost_breakup = pg_fields.JSONField(default={}, editable=False)

    Const = constants

    class Meta(BaseModel.Meta):
        db_table = 'cart'

    @property
    def total(self):
        return round(self.subtotal + self.shipping_charge + self.additional_charge, 2)

    def calculate_cost(self, force_item_calculation=True):
        """
        :return:
        """
        self.subtotal = 0.0
        self.shipping_charge = 0.0
        self.additional_charge = 0.0
        self.cost_breakup = {}
        additional_charge = {}

        # Count rental products
        for item in self.rentalitem_set.all():
            if force_item_calculation is True:
                item.calculate_cost()
            if item.is_postpaid is True:
                continue

            self.shipping_charge += item.shipping_charge
            self.subtotal += item.subtotal
            self.additional_charge += item.additional_charge

            for k, v in item.cost_breakup['additional_charge'].items():
                # Initialize value
                if additional_charge.get(k, None) is None:
                    additional_charge[k] = 0.0
                additional_charge[k] += v

        # Count purchase products
        for item in self.purchaseitem_set.all():
            if force_item_calculation is True:
                item.calculate_cost()

            self.shipping_charge += item.shipping_charge
            self.subtotal += item.subtotal
            self.additional_charge += item.additional_charge

            for k, v in item.cost_breakup['additional_charge'].items():
                # Initialize value
                if additional_charge.get(k, None) is None:
                    additional_charge[k] = 0.0
                additional_charge[k] += v

        self.cost_breakup['sales_tax_pct'] = getattr(self.get_sales_tax(), 'value', 0)
        self.cost_breakup['additional_charge'] = additional_charge

        self.save(update_fields=['cost_breakup', 'shipping_charge', 'subtotal',
                                 'additional_charge'])

    def get_sales_tax(self):
        """
        :return: Get sales tax percentage
        """
        try:
            tax = SalesTax.objects.get(country=self.location.country, state=self.location.state)
        except SalesTax.DoesNotExist:
            return None
        except AttributeError:
            L.debug('Cart location is not set', extra={'cart': self.id})
            return None
        else:
            return tax

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    @transaction.atomic
    def checkout(self):
        L.info('Checking out the cart')
        if self.is_active is False:
            L.warning(messages.ERR_CHKT_CART_INACTIVE[0])
            raise errors.CartError(*messages.ERR_CHKT_CART_INACTIVE)

        if self.location is None:
            L.warning(messages.ERR_CHKT_NO_SHIPPING_ADDR[0])
            raise errors.CartError(*messages.ERR_CHKT_NO_SHIPPING_ADDR)

        if self.billing_address is None:
            L.warning(messages.ERR_CHKT_NO_BILLING_ADDR[0])
            raise errors.CartError(*messages.ERR_CHKT_NO_BILLING_ADDR)

        if self.rentalitem_set.count() == 0 and self.purchaseitem_set.count() == 0:
            L.warning(messages.ERR_CHKT_NO_ITEM[0])
            raise errors.CartError(*messages.ERR_CHKT_NO_ITEM)

        order = Order.objects.create_order(self)
        invoice = Invoice.objects.create_from_order(order)

        return order, invoice


class Item(BaseModel):
    SHIPPING_KIND = (
        (ship_const.SHIPPING_PICKUP, 'Pickup'),
        (ship_const.SHIPPING_DELIVERY, 'Delivery'),
    )

    cart = models.ForeignKey('Cart')
    product = models.ForeignKey('catalog.Product')
    #: How shipping will be made?
    shipping_kind = models.CharField(max_length=20, choices=SHIPPING_KIND)
    #: Subtotal
    subtotal = ex_fields.FloatField(min_value=0.0, max_value=99999999, precision=2, default=0)
    #: Shipping cost
    shipping_charge = ex_fields.FloatField(min_value=0.0, max_value=999999, precision=2, default=0)
    #: Additional charges including sales tax
    additional_charge = ex_fields.FloatField(default=0, min_value=0.0)
    #: Is the is product shippable to cart location
    is_shippable = models.BooleanField(default=False)
    #: Item quantity
    qty = models.PositiveSmallIntegerField(default=1)
    #: Cost breakup
    cost_breakup = pg_fields.JSONField(default={'additional_charge': {}}, editable=False)

    class Meta(BaseModel.Meta):
        abstract = True

    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)

        self.calc = Calculator(self.product, self.qty)

    @property
    def shipping_method(self):
        return self.product.get_standard_shipping_method(self.cart.location)

    @property
    def total(self):
        return round(self.subtotal + self.shipping_charge + self.additional_charge, 2)

    def calculate_cost(self):
        """
        Calculates the cost of rent, shipping (according to qty) and sales tax
        """
        # Subtotal of either rent or purchase
        subtotal = self._calculate_subtotal()
        self.subtotal = subtotal['amt']

        # Shipping charge
        shipping = self._calculate_shipping_cost()
        self.shipping_charge = shipping['amt']

        # Additional charge
        additional_charge = self._calculate_additional_charge(
            AdditionalCharge.Const.ItemKind.RENTAL
        )
        self.additional_charge = additional_charge['amt']

        # Cost breakup
        self.cost_breakup['subtotal'] = subtotal
        self.cost_breakup['shipping'] = shipping
        self.cost_breakup['additional_charge'] = additional_charge

        self.save(update_fields=['cost_breakup', 'shipping_charge', 'subtotal',
                                 'additional_charge'])

    def _calculate_subtotal(self):
        raise NotImplementedError

    def _calculate_shipping_cost(self):
        data = self.calc.calc_shipping_charge(self.cart.location, self.shipping_kind)

        L.info('Shipping cost', extra=data)

        return data

    def _calculate_sales_tax(self, amt):
        sales_tax = self.cart.get_sales_tax()

        tax = self.calc.calc_sales_tax(amt, sales_tax)

        return tax

    def _calculate_additional_charge(self, item_kind):
        """
        Calculates any additional charges levied by seller and sales tax

        :return dict:
        """

        # Sales tax
        sales_tax = self._calculate_sales_tax(self.subtotal + self.shipping_charge)
        data = self.calc.calc_additional_charge(self.subtotal, item_kind, {
            'sales_tax': sales_tax['amt']
        })

        return data


class RentalItem(Item):
    # Item to be delivered by
    date_start = models.DateTimeField(validators=[validate_date_start])
    # Item to be returned
    date_end = models.DateTimeField()
    #: Should pay later?
    is_postpaid = models.BooleanField(default=True)

    class Meta(Item.Meta):
        unique_together = ('cart', 'product', 'date_start', 'date_end')

    def _calculate_subtotal(self):
        """
        Calculate product rent for date_start and date_end range

        :return Dict:
            {
                'rent_per': rent_per, 'product': self.product.id, 'cart': self.cart.id,
                'daily_rent': daily_rent, 'rent': rent, 'num_days': num_days, 'rent_days': rent_days
            }
        """
        data = self.calc.calc_rent(self.date_start, self.date_end)

        ex = dict(data.items() + {'cart': self.cart_id, 'qty': self.qty}.items())
        L.info('Rent calculation', extra=ex)

        return data


class PurchaseItem(Item):
    class Meta(Item.Meta):
        unique_together = ('cart', 'product')

    def _calculate_subtotal(self):
        """
        Calculates the cost of item, shipping (according to qty) and sales tax
        """
        return {'amt': self.product.sell_price * self.qty, 'unit_price': self.product.sell_price}
