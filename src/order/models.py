from django.db import models, transaction
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseModel, DateTimeFieldMixin, BaseManager
from shipping import constants as ship_const
from . import errors, messages, constants


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
                    and item.shipping_kind == ship_const.SHIPPING_DELIVERY):
                    raise errors.OrderError(*messages.ERR_NON_SHIPPABLE)

                if not item.shipping_kind:
                    raise errors.OrderError(messages.ERR_MISS_SHIPPING_KIND[0] % item.product.name,
                                            messages.ERR_MISS_SHIPPING_KIND[1])

                orderline = OrderLine.objects.get_or_create(user=item.product.user, order=order)[0]

                product_serializer = ProductSerializer(item.product)
                RentalItem.objects.create(
                    order=order,
                    orderline=orderline,
                    qty=item.qty,
                    user=cart.user,
                    shipping_kind=item.shipping_kind,
                    detail=product_serializer.data,
                    shipping_method=item.shipping_method.name if item.shipping_method else None,
                    date_start=item.date_start,
                    date_end=item.date_end,
                    subtotal=item.subtotal,
                    cost_breakup=item.cost_breakup
                )

            # Make cart inactive
            cart.deactivate()

            # Calculate orderline cost
            for orderline in order.orderline_set.all():
                orderline.calculate_cost()

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
    total = pg_fields.JSONField()

    objects = OrderManager()

    class Meta(BaseModel.Meta):
        db_table = 'order'
        ordering = ['-id']


class OrderLine(BaseModel, DateTimeFieldMixin):
    """
    This class represents the order to be fulfilled by the seller, i.e. it has items grouped by
    seller
    """
    #: Seller user id
    user = models.ForeignKey('miniauth.User')
    #: Order id
    order = models.ForeignKey('Order')
    #: Total amount of this line
    total = pg_fields.JSONField(null=True, default=None)

    def calculate_cost(self):
        total = {'subtotal': 0.0, 'sales_tax': 0.0, 'shipping': 0.0}

        for item in self.rentalitem_set.all():
            total['subtotal'] += item.subtotal
            total['sales_tax'] += item.cost_breakup['sales_tax']['amt']
            total['shipping'] += item.cost_breakup['shipping']['amt']

        total['total'] = round(total['subtotal'] + total['sales_tax'] + total['shipping'], 2)

        self.total = total
        self.save(update_fields=['total'])


class Item(BaseModel):
    STATUS = (
        (constants.STATUS_REQUEST, 'Requested'),
        (constants.STATUS_APPROVE, 'Approved'),
        (constants.STATUS_DISPATCH, 'Dispatched'),
        (constants.STATUS_READY, 'Ready to ship'),
        (constants.STATUS_DELIVERED, 'Delivered'),
    )
    #: Reference to order
    order = models.ForeignKey(Order)
    orderline = models.ForeignKey(OrderLine)
    #: The user who has ordered
    user = models.ForeignKey('miniauth.User')
    #: Inventory that is assigned to the item
    inventory = models.ForeignKey('catalog.Inventory', null=True, default=None)
    #: Product detail, copied from cart rental item
    detail = pg_fields.JSONField()
    #: The rental item status order
    status = models.CharField(max_length=30, default=constants.STATUS_REQUEST, choices=STATUS)
    #: Subtotal, only includes rent for quantity
    subtotal = models.FloatField()
    #: Subtotal breakup
    cost_breakup = pg_fields.JSONField()
    #: Quantity
    qty = models.PositiveSmallIntegerField()
    #: Shipping kind
    shipping_kind = models.CharField(max_length=20)
    #: Shipping method
    shipping_method = models.CharField(max_length=30, null=True)
    #: Payment method, postpaid for now
    payment_method = models.CharField(max_length=20, default='postpaid')

    class Meta(BaseModel.Meta):
        abstract = True


class RentalItem(Item):
    #: Rental period
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
