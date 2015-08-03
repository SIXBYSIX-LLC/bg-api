import logging

from django.db import models
from django.utils.text import slugify
from djangofuture.contrib.postgres import fields as pg_fields

from cart.validators import validate_date_start
from common.models import BaseManager, BaseModel, DateTimeFieldMixin
from common import fields as ex_fields
from charge.models import SalesTax, AdditionalCharge
from . import constants
from shipping import constants as ship_const

L = logging.getLogger('bgapi.' + __name__)


class CartManager(BaseManager):
    pass


class Cart(BaseModel, DateTimeFieldMixin):
    rental_products = models.ManyToManyField('catalog.Product', through='RentalItem',
                                             related_name='+')
    purchase_products = models.ManyToManyField('catalog.Product', through='PurchaseItem',
                                               related_name='+')
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
                if self.cost_breakup.get(k, None) is None:
                    self.cost_breakup[k] = 0.0
                self.cost_breakup[k] += v

        # Count purchase products
        for item in self.purchaseitem_set.all():
            if force_item_calculation is True:
                item.calculate_cost()

            self.shipping_charge += item.shipping_charge
            self.subtotal += item.subtotal
            self.additional_charge += item.additional_charge

            for k, v in item.cost_breakup['additional_charge'].items():
                # Initialize value
                if self.cost_breakup.get(k, None) is None:
                    self.cost_breakup[k] = 0.0
                self.cost_breakup[k] += v

        self.cost_breakup['sales_tax_pct'] = getattr(self.get_sales_tax(), 'value', 0)

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
    cost_breakup = pg_fields.JSONField(default={}, editable=False)

    class Meta(BaseModel.Meta):
        abstract = True

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
        data = {'amt': 0.0}

        if self.shipping_kind == ship_const.SHIPPING_PICKUP:
            L.info('Shipping cost', extra=data)
            return data
        if self.is_shippable is False:
            L.info('Item is not shippable', extra={
                'cart': self.cart_id, 'product': self.product_id
            })
            return data

        # Shipping standard method
        data['amt'] = round(self.shipping_method.cost * self.qty, 2)
        data['method'] = 'standard_shipping'
        data['id'] = self.shipping_method.id

        L.info('Shipping cost', extra=data)

        return data

    def _calculate_sales_tax(self, amt):
        tax = {'pct': 0, 'amt': 0.0}
        sales_tax = self.cart.get_sales_tax()

        if sales_tax:
            tax['taxable_amt'] = amt
            tax['id'] = sales_tax.id
            tax['pct'] = sales_tax.value
            tax['amt'] = round((amt * sales_tax.value) / 100, 2)

        return tax

    def _calculate_additional_charge(self, item_kind):
        """
        Calculates any additional charges levied by seller and sales tax

        :return dict:
        """
        data = {'amt': 0.0}
        charge_const = AdditionalCharge.Const
        charges = AdditionalCharge.objects.all_by_natural_key(
            self.product.user, item_kind, self.product.category
        )

        for charge in charges:
            k = slugify(charge.name).replace('-', '_')
            if charge.unit == charge_const.Unit.FLAT:
                data[k] = charge.value
                data['amt'] += charge.value * self.qty
            elif charge.unit == charge_const.Unit.PERCENTAGE:
                value = round((self.subtotal * charge.value) / 100, 2)
                data[k] = value
                data['amt'] += value * self.qty

        # Sales tax
        sales_tax = self._calculate_sales_tax(self.subtotal + self.shipping_charge)
        data['sales_tax'] = sales_tax['amt']

        # Add sales tax amount to total amount
        data['amt'] += sales_tax['amt']

        return data


class RentalItem(Item):
    # Item to be delivered by
    date_start = models.DateTimeField(validators=[validate_date_start])
    # Item to be returned
    date_end = models.DateTimeField()
    #: Should pay later?
    is_postpaid = models.BooleanField(default=False)

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
        num_days = (self.date_end - self.date_start).days
        user_settings = self.product.user.profile.settings

        daily_rental_till = user_settings.get('daily_price_till_days') or 3
        weekly_rental_till = user_settings.get('weekly_price_till_days') or 25

        # Decide which rental cost should be applied
        if daily_rental_till < num_days <= weekly_rental_till:
            rent_per = self.product.weekly_price
            rent_days = 7
        elif num_days > weekly_rental_till:
            rent_per = self.product.monthly_price
            rent_days = 30
        else:
            rent_per = self.product.daily_price
            rent_days = 1

        # Getting daily rent from unit rent
        daily_rent = rent_per / rent_days
        # Final rent
        rent = round(daily_rent * num_days * self.qty, 2)

        data = {
            'rent_per': rent_per, 'daily_rent': daily_rent, 'amt': rent, 'num_days': num_days,
            'rent_unit_days': rent_days, 'unit_price': daily_rent * num_days
        }

        ex = dict(data.items() + {'cart': self.cart_id, 'qty': self.qty}.items())
        L.info('Rent calculation', extra=ex)

        return data


class PurchaseItem(Item):
    def _calculate_subtotal(self):
        """
        Calculates the cost of item, shipping (according to qty) and sales tax
        """
        return {'amt': self.product.sell_price * self.qty, 'unit_price': self.product.sell_price}
