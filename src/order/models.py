from django.db import models, transaction
from djangofuture.contrib.postgres import fields as pg_fields
from model_utils.managers import InheritanceManager

from common.models import BaseModel, DateTimeFieldMixin, BaseManager
from shipping import constants as ship_const
from . import messages, signals
from common import errors
from constants import Status as sts_const


class OrderManager(BaseManager):
    def create_order(self, cart):

        def check_shipping(item):
            # Check if not any non-shippable item
            if (item.is_shippable is False
                and item.shipping_kind == ship_const.SHIPPING_DELIVERY):
                raise errors.OrderError(*messages.ERR_NON_SHIPPABLE)

            if not item.shipping_kind:
                raise errors.OrderError(messages.ERR_MISS_SHIPPING_KIND[0] % item.product.name,
                                        messages.ERR_MISS_SHIPPING_KIND[1])

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

            # Rental Item
            for item in cart.rentalitem_set.all():
                check_shipping(item)

                orderline = OrderLine.objects.get_or_create(user=item.product.user, order=order)[0]

                product_serializer = ProductSerializer(item.product)

                rental_item = RentalItem.objects.create(
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
                    cost_breakup=item.cost_breakup,
                    is_postpaid=item.is_postpaid
                )
                rental_item.change_status(sts_const.NOT_CONFIRMED)

            # Purchase Item
            for item in cart.purchaseitem_set.all():
                check_shipping(item)

                orderline = OrderLine.objects.get_or_create(user=item.product.user, order=order)[0]

                product_serializer = ProductSerializer(item.product)

                purchase_item = PurchaseItem.objects.create(
                    order=order,
                    orderline=orderline,
                    qty=item.qty,
                    user=cart.user,
                    shipping_kind=item.shipping_kind,
                    detail=product_serializer.data,
                    shipping_method=item.shipping_method.name if item.shipping_method else None,
                    subtotal=item.subtotal,
                    cost_breakup=item.cost_breakup
                )
                purchase_item.change_status(sts_const.NOT_CONFIRMED)

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

    @property
    def rentalitem_set(self):
        return RentalItem.objects.filter(order=self)

    @property
    def purchaseitem_set(self):
        return PurchaseItem.objects.filter(order=self)


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

        for item in self.item_set.select_related('rentalitem').all():
            if getattr(item, 'rentalitem', None):
                if item.rentalitem.is_postpaid:
                    continue

            total['subtotal'] += item.subtotal
            total['sales_tax'] += item.cost_breakup['sales_tax']['amt']
            total['shipping'] += item.cost_breakup['shipping']['amt']

        total['total'] = round(total['subtotal'] + total['sales_tax'] + total['shipping'], 2)

        self.total = total
        self.save(update_fields=['total'])

    @property
    def rentalitem_set(self):
        return RentalItem.objects.filter(orderline=self)

    @property
    def purchaseitem_set(self):
        return PurchaseItem.objects.filter(orderline=self)


class Item(BaseModel):
    #: Reference to order
    order = models.ForeignKey(Order)
    orderline = models.ForeignKey(OrderLine)
    #: The user who has ordered
    user = models.ForeignKey('miniauth.User')
    #: Inventory that is assigned to the item
    inventories = models.ManyToManyField('catalog.Inventory')
    #: Product detail, copied from cart rental item
    detail = pg_fields.JSONField()
    #: Item status
    statuses = models.ManyToManyField('Status')
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

    objects = InheritanceManager()

    @property
    def current_status(self):
        return self.statuses.last()

    def change_status(self, status, comment=None, **kwargs):
        """
        Change item status

        :param status: New status
        :param comment: Comment if any
        :raise ChangeStatusError:
        """
        old_status = self.current_status
        signals.pre_status_change.send(instance=self, new_status=status, old_status=old_status)

        # Check if new status can be changed from old status
        changeable_to = Status.CHANGEABLE_TO.get(getattr(self.current_status, 'status', None), [])
        if self.current_status and status not in changeable_to:
            raise errors.ChangeStatusError(*messages.ERR_NOT_CHANGEABLE)

        # Validate and modify if new status is approved
        if status == sts_const.APPROVED:
            self.__change_status_approve()

        self.statuses.add(Status.objects.create(status=status, comment=comment))

        signals.pre_status_change.send(instance=self, new_status=status, old_status=old_status)

    def add_inventories(self, *inventories):
        """
        Add inventories to this item

        :param Inventory inventories: Inventory object
        :return: None
        :raise InventoryError:
        """
        for inventory in inventories:
            if inventory.is_active is False:
                raise errors.InventoryError(*messages.ERR_INACTIVE_INVENTORY)

        self.inventories.add(*inventories)
        self.inventories.update(is_active=False)

    def __change_status_approve(self):
        if self.inventories.count() != self.qty:
            raise errors.ChangeStatusError(*messages.ERR_NO_INVENTORIES)


class RentalItem(Item):
    #: Rental period
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    #: Is payment is postpaid
    is_postpaid = models.BooleanField()


class PurchaseItem(Item):
    pass


class Status(BaseModel, DateTimeFieldMixin):
    CHANGEABLE_TO = {
        sts_const.NOT_CONFIRMED: [sts_const.CONFIRMED],
        sts_const.CONFIRMED: [sts_const.APPROVED, sts_const.CANCEL],
        sts_const.APPROVED: [sts_const.PICKED_UP, sts_const.READY_TO_SHIP,
                             sts_const.READY_TO_PICKUP, sts_const.CANCEL],
        sts_const.READY_TO_SHIP: [sts_const.DISPATCHED, sts_const.CANCEL],
        sts_const.DISPATCHED: [sts_const.DELIVERED],
        sts_const.READY_TO_PICKUP: [sts_const.PICKED_UP],
        sts_const.CANCEL: [],
        sts_const.PICKED_UP: [],
        sts_const.DELIVERED: [],
    }
    STATUS = [(getattr(sts_const, prop), getattr(sts_const, prop))
              for prop in dir(sts_const) if prop.startswith('_') is False]

    #: The rental item status order
    status = models.CharField(max_length=30, choices=STATUS)
    comment = models.TextField(null=True, default=None)

    Const = sts_const
