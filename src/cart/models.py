import logging

from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseManager, BaseModel, DateTimeFieldMixin
from . import constants, signals
from tax.models import SalesTax

L = logging.getLogger('bgapi.' + __name__)


class CartManager(BaseManager):
    pass


class Cart(BaseModel, DateTimeFieldMixin):
    rental_products = models.ManyToManyField('catalog.Product', through='RentalItem')
    #: Shipping Location
    location = models.ForeignKey('usr.Address', null=True, default=None)
    #: Cart owner
    user = models.ForeignKey('miniauth.User', blank=True, editable=False)
    #: This value can be false in case it's converted to order or by other conditions in future
    is_active = models.BooleanField(default=True, editable=False)
    #: Total estimated cost to be paid
    total = pg_fields.JSONField(editable=False, default={})

    Const = constants

    class Meta(BaseModel.Meta):
        db_table = 'cart'

    def calculate_cost(self):
        """
        Total
        Sales tax
        Environment fee
        :return:
        """
        total = {'subtotal': 0.0}

        # Count products
        for product in self.rental_products:
            total['subtotal'] += product.subtotal

        total['sales_tax_pct'] = self.get_sales_tax()
        total['sales_tax'] = (total['subtotal'] * self.get_sales_tax()) / 100
        total['total'] = total['subtotal'] + total['sales_tax']

        self.total = total

        signals.pre_cost_calculation.send(instance=self)

        self.save(update_fields=['total'])

        signals.post_cost_calculation.send(instance=self)

    def get_sales_tax(self):
        """
        :return: Get sales tax percentage
        """
        try:
            tax = SalesTax.objects.get(country=self.location.country, state=self.location.state)
        except SalesTax.DoesNotExist:
            return 0.0
        else:
            return tax.value


class Item(BaseModel):
    SHIPPING_KIND = (
        (constants.SHIPPING_PICKUP, 'Pickup'),
        (constants.SHIPPING_DELIVERY, 'Delivery'),
    )

    cart = models.ForeignKey('Cart')
    product = models.ForeignKey('catalog.Product')
    #: How shipping will be made?
    shipping_kind = models.CharField(max_length=20, choices=SHIPPING_KIND)
    #: Shipping cost
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    #: sub total
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    #: Is the is product shippable to cart location
    is_shippable = models.BooleanField(default=False)
    # Item quantity
    qty = models.PositiveSmallIntegerField(default=1)

    class Meta(BaseModel.Meta):
        abstract = True


class RentalItem(Item):
    # Item to be delivered by
    date_start = models.DateTimeField()
    # Item to be returned
    date_end = models.DateTimeField()
    #: Rent
    cost_breakup = pg_fields.JSONField(default={}, editable=False)

    class Meta(Item.Meta):
        unique_together = ('cart', 'product', 'date_start', 'date_end')

    def calculate_cost(self):
        """
        Shipping cost
        Rent according to date range
        :return:
        """
        self.cost_breakup['rent'] = self._calculate_rent()
        self.cost_breakup['shipping'] = self._calculate_shipping_cost()

        self.shipping_cost = self.cost_breakup['shipping_cost']
        self.subtotal = self.shipping_cost + self.cost_breakup['rent']

        signals.pre_cost_calculation.send(instance=self)

        self.save(update_fields=['cost_breakup', 'shipping_cost', 'subtotal'])

        signals.post_cost_calculation.send(instance=self)

    def _calculate_shipping_cost(self):
        data = {'shipping_cost': 0.0}

        if self.shipping_kind == constants.SHIPPING_PICKUP:
            L.info('Shipping cost', extra=data)
            return data

        # Shipping standard method
        standard_method = self.product.get_standard_shipping_method(self.cart.location)

        data['shipping_cost'] = standard_method.cost
        data['shipping_method'] = 'standard_shipping'
        data['method_id'] = standard_method.id

        L.info('Shipping cost', extra=data)

        return data

    def _calculate_rent(self):
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
        rent = daily_rent * num_days

        data = {
            'rent_per': rent_per, 'product': self.product.id, 'cart': self.cart.id,
            'daily_rent': daily_rent, 'rent': rent, 'num_days': num_days, 'rent_days': rent_days
        }

        L.info('Rent calculation', extra=data)

        return data

