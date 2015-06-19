from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseManager, BaseModel
from . import constats


class ProductManager(BaseManager):
    pass


class Product(BaseModel):
    """
    Product information that are to be shown to buyer
    """

    CONDITION = (
        (constats.Product.CONDITION_NEW, 'New'),
        (constats.Product.CONDITION_USED, 'Used'),
    )

    #: Product name
    name = models.CharField(max_length=100)
    #: Product images, up to 10
    images = pg_fields.ArrayField(models.URLField(), 10, blank=True, null=True)
    #: Product description
    description = models.TextField(blank=True, null=True)
    #: Brand
    brand = models.CharField(max_length=100)
    #: Daily rental price
    daily_price = models.FloatField()
    #: Weekly rental price
    weekly_price = models.FloatField()
    #: Monthly rental price
    monthly_price = models.FloatField()
    #: Selling price
    sell_price = models.FloatField()
    #: Product category
    category = models.ForeignKey('Category')
    #: Is active and searchable
    is_active = models.BooleanField(blank=True, default=False)
    #: Product location
    location = models.ForeignKey('Address')
    #: SKU id, auto generated in-case of received blank
    sku = models.CharField(max_length=30, blank=True)
    #: Additional attributes
    attributes = pg_fields.JSONField(null=True, blank=True)
    #: Search tags
    tags = pg_fields.ArrayField(models.CharField(), blank=True, null=True)
    #: User
    user = models.ForeignKey('miniauth.User')
    #: Condition
    condition = models.CharField(choices=CONDITION)
    date_created_at = models.DateTimeField(auto_now_add=True, blank=True, editable=False)
    date_updated_at = models.DateTimeField(auto_now=True, blank=True, editable=False)

    objects = ProductManager()

    class Meta(BaseModel.Meta):
        unique_together = ('user', 'sku')


class InventoryManager(BaseManager):
    pass


class Inventory(BaseModel):
    """
    Inventory for products
    """
    SOURCE = (
        (constats.Inventory.SOURCE_PURCHASED, 'Purchased'),
        (constats.Inventory.SOURCE_RENTED, 'Rented from others'),
    )

    product = models.ForeignKey(Product)
    serial_no = models.CharField(max_length=50, blank=True, null=True)
    #: The source of inventory, either owned, re-rent from others
    source = models.CharField(choices=SOURCE, default='purchased', blank=True)
    #: Is inventory available
    is_active = models.BooleanField()
    date_created_at = models.DateTimeField(auto_now_add=True, blank=True, editable=False)

    objects = InventoryManager()

    Const = constats.Inventory
