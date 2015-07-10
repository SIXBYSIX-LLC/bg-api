import logging

from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields

from cart.validators import validate_date_start
from common.models import BaseManager, BaseModel, DateTimeFieldMixin
from common import fields as ex_fields
from tax.models import SalesTax
from . import constants
from shipping import constants as ship_const

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

    def calculate_cost(self, force_item_calculation=True):
        """
        Total
        Sales tax
        Environment fee
        :return:
        """
        total = {'subtotal': 0.0, 'sales_tax': 0.0, 'shipping': 0.0}

        # Count products
        for item in self.rentalitem_set.all():
            if force_item_calculation is True:
                item.calculate_cost()

            total['subtotal'] += item.subtotal
            total['sales_tax'] += item.cost_breakup['sales_tax']['amt']
            total['shipping'] += item.shipping_cost

        total['sales_tax_pct'] = getattr(self.get_sales_tax(), 'value', 0)
        total['total'] = round(total['subtotal'] + total['sales_tax'] + total['shipping'], 2)

        self.total = total
        self.save()

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
    #: Shipping cost
    shipping_cost = ex_fields.FloatField(min_value=0.0, max_value=999999, precision=2, default=0)
    #: sub total
    subtotal = ex_fields.FloatField(min_value=0.0, max_value=99999999, precision=2, default=0)
    #: Is the is product shippable to cart location
    is_shippable = models.BooleanField(default=False)
    # Item quantity
    qty = models.PositiveSmallIntegerField(default=1)

    class Meta(BaseModel.Meta):
        abstract = True

    @property
    def shipping_method(self):
        return self.product.get_standard_shipping_method(self.cart.location)


class RentalItem(Item):
    # Item to be delivered by
    date_start = models.DateTimeField(validators=[validate_date_start])
    # Item to be returned
    date_end = models.DateTimeField()
    #: Rent
    cost_breakup = pg_fields.JSONField(default={}, editable=False)

    class Meta(Item.Meta):
        unique_together = ('cart', 'product', 'date_start', 'date_end')

    def calculate_cost(self):
        """
        Calculates the cost of rent, shipping (according to qty) and sales tax
        """
        rent = self._calculate_rent()
        shipping = self._calculate_shipping_cost()
        sales_taxable_amt = rent['amt'] + shipping['amt']
        sales_tax = self._calculate_sales_tax(sales_taxable_amt)

        self.cost_breakup['rent'] = rent
        self.cost_breakup['shipping'] = shipping
        self.cost_breakup['sales_tax'] = sales_tax

        self.subtotal = rent['amt']
        self.shipping_cost = shipping['amt']

        self.save(update_fields=['cost_breakup', 'shipping_cost', 'subtotal'])

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
        rent = round(daily_rent * num_days * self.qty, 2)

        data = {
            'rent_per': rent_per, 'daily_rent': daily_rent, 'amt': rent, 'num_days': num_days,
            'rent_unit_days': rent_days
        }

        ex = dict(data.items() + {'cart': self.cart_id, 'qty': self.qty}.items())
        L.info('Rent calculation', extra=ex)

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

