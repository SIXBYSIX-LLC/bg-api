from django.db import models, transaction
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseModel, DateTimeFieldMixin, BaseManager
from shipping import constants as ship_const
from . import errors, messages
from common import fields as ex_fields


class OrderManager(BaseManager):
    def create_order(self, cart):
        with transaction.atomic():
            # Creating order
            order = self.model(cart=cart, user=cart.user)
            order.address = "%s\n\n%s" % (cart.location.address1, cart.location.address2)
            order.country = cart.location.country
            order.state = cart.location.state
            order.city = cart.location.city
            order.zip_code = cart.location.zip_code
            order.total = cart.total
            order.save()

            # Creating RentalItem
            from catalog.serializers import ProductSerializer

            for item in cart.rentalitem_set.all():
                # Check if not any non-shippable item
                if (item.is_shippable is False
                    and cart.shipping_kind == ship_const.SHIPPING_DELIVERY):
                    raise errors.OrderError(*messages.ERR_NON_SHIPPABLE)

                product_serializer = ProductSerializer(item.product)
                RentalItem.objects.create(
                    order=order,
                    to_user=item.product.user,
                    qty=item.qty,
                    shipping_kind=cart.shipping_kind,
                    detail=product_serializer.data,
                    shipping_method=item.shipping_method.name,
                    date_start=item.date_start,
                    date_end=item.date_end,
                    subtotal=item.subtotal,
                    cost_breakup=item.cost_breakup
                )

            # Make cart inactive
            cart.deactiveate()

        return order


class Order(BaseModel, DateTimeFieldMixin):
    # Cart, just for reference
    cart = models.ForeignKey('cart.Cart')
    # The user, who is creating the order
    user = models.ForeignKey('miniauth.User')
    # Address, copied from cart
    address = models.TextField()
    country = models.ForeignKey('cities.Country')
    state = models.ForeignKey('cities.Region')
    city = models.ForeignKey('cities.City')
    zip_code = models.CharField(max_length=15)
    #: total order value
    total = ex_fields.FloatField(min_value=0.0, max_value=99999999, precision=2, default=0.0)

    objects = OrderManager()

    class Meta(BaseModel.Meta):
        db_table = 'order'
        ordering = ['-id']


class Item(BaseModel):
    #: Reference to order
    order = models.ForeignKey(Order)
    #: The user who is going to fulfill the item
    to_user = models.ForeignKey('miniauth.User')
    #: Inventory that is assigned to the item
    inventory = models.ForeignKey('catalog.Inventory', null=True, default=None)
    #: Product detail, copied from cart rental item
    detail = pg_fields.JSONField()
    #: The rental item status order
    is_approved = models.NullBooleanField(default=None)
    is_prepared = models.BooleanField(default=False)
    is_dispatched = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    #: Subtotal including tax
    subtotal = models.FloatField()
    #: Subtotal breakup
    cost_breakup = pg_fields.JSONField()
    #: Quantity
    qty = models.PositiveSmallIntegerField()
    #: Shipping kind
    shipping_kind = models.CharField(max_length=20)
    #: Shipping method
    shipping_method = models.CharField(max_length=30)
    #: Payment method, postpaid for now
    payment_method = models.CharField(max_length=20, default='postpaid')

    class Meta(BaseModel.Meta):
        abstract = True


class RentalItem(BaseModel):
    #: Rental period
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
