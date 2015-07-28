from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields
from django.core.exceptions import ValidationError

from common.models import BaseManager, BaseModel
from common import fields as ex_fields
from . import constats, messages


def validate_category_is_leaf(value):
    if value.category_set.count() > 0:
        raise ValidationError(*messages.ERR_NOT_LEAF_CATEGORY)


class ProductManager(BaseManager):
    def create_product(self, **kwargs):
        """
        Create product same way as .create() method. Only difference is it creates inventories
        from qty field
        """
        qty = kwargs.pop('qty', 0)

        # Create product object
        product = self.create(**kwargs)

        # Adding inventory
        if qty > 0:
            inventories = [Inventory(source=constats.Inventory.SOURCE_PURCHASED, user=product.user,
                                     product=product, is_active=True) for i in xrange(qty)]
            product.inventory_set.add(*inventories)

        return product

    def search(self, query, raw=False):
        function = "to_tsquery" if raw else "plainto_tsquery"
        search_vector = "name || ' ' || array_to_string(tags, ' ')"
        ts_query = "%s(%s)" % (function, '%s')
        where = "to_tsvector(%s) @@ %s" % (search_vector, ts_query)
        where += " OR name LIKE %s OR array_to_string(tags, ' ') LIKE %s"

        return self.extra(where=[where], params=[query, '%' + query + '%', '%' + query + '%'])



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
    images = models.ManyToManyField('static.File', blank=True)
    #: Product description
    description = models.TextField(blank=True, null=True)
    #: Brand
    brand = models.CharField(max_length=100)
    #: Daily rental price
    daily_price = ex_fields.FloatField(min_value=0.0, max_value=99999, precision=2)
    #: Weekly rental price
    weekly_price = ex_fields.FloatField(min_value=0.0, max_value=999999, precision=2)
    #: Monthly rental price
    monthly_price = ex_fields.FloatField(min_value=0.0, max_value=9999999, precision=2)
    #: Selling price
    sell_price = ex_fields.FloatField(min_value=0.0, max_value=999999999, precision=2)
    #: Product category
    category = models.ForeignKey('category.Category', validators=[validate_category_is_leaf])
    #: Is active and searchable
    is_active = models.BooleanField(blank=True, default=False)
    #: Product location
    location = models.ForeignKey('usr.Address')
    #: SKU id, auto generated in-case of received blank
    sku = models.CharField(max_length=30, blank=True, default=None)
    #: Additional attributes
    attributes = pg_fields.JSONField(null=True, blank=True)
    #: Search tags
    tags = pg_fields.ArrayField(models.CharField(max_length=100), blank=True, null=True)
    #: User
    user = models.ForeignKey('miniauth.User', editable=False, blank=True, default=None)
    #: Condition
    condition = models.CharField(choices=CONDITION, max_length=50)
    date_created_at = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated_at = models.DateTimeField(auto_now=True, editable=False)

    objects = ProductManager()

    class Meta(BaseModel.Meta):
        unique_together = ('user', 'sku')

    def get_standard_shipping_method(self, to_location):
        user = self.user
        try:
            return user.standardmethod_set.filter(
                origin=self.location,
                country=to_location.country,
                zipcode_start__lte=int(to_location.zip_code),
                zipcode_end__gte=int(to_location.zip_code),
            ).first()
        except AttributeError:
            return None


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
    source = models.CharField(choices=SOURCE, default='purchased', blank=True, max_length=50)
    #: Is inventory available
    is_active = models.BooleanField()
    date_created_at = models.DateTimeField(auto_now_add=True, blank=True, editable=False)
    user = models.ForeignKey('miniauth.User', editable=False, blank=True, default=None)

    objects = InventoryManager()

    Const = constats.Inventory

    class Meta(BaseModel.Meta):
        unique_together = ('product', 'serial_no')
