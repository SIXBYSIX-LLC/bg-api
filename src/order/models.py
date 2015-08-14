import logging

from django.db import models, transaction
from django.db.models import Q
from django.utils.crypto import get_random_string
from djangofuture.contrib.postgres import fields as pg_fields
from model_utils.managers import InheritanceManager

from catalog.models import Product
from charge.models import Calculator
from common.models import BaseModel, DateTimeFieldMixin, BaseManager, AddressBase
from shipping import constants as ship_const
from . import messages, signals
from common import errors, fields as ex_fields
from constants import Status as sts_const

L = logging.getLogger('bgapi.' + __name__)


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
            # Copy address
            shipping_address = Address(**self.model_to_dict(cart.location))
            shipping_address.name = get_random_string()
            shipping_address.save()

            billing_address = Address(**self.model_to_dict(cart.billing_address))
            billing_address.name = get_random_string()
            billing_address.save()

            # Creating order
            order = self.model(cart=cart, user=cart.user)
            order.subtotal = cart.subtotal
            order.shipping_charge = cart.shipping_charge
            order.additional_charge = cart.additional_charge
            order.cost_breakup = cart.cost_breakup
            order.shipping_address = shipping_address
            order.billing_address = billing_address
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
                    shipping_charge=item.shipping_charge,
                    additional_charge=item.additional_charge,
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
                    shipping_charge=item.shipping_charge,
                    additional_charge=item.additional_charge,
                    cost_breakup=item.cost_breakup
                )
                purchase_item.change_status(sts_const.NOT_CONFIRMED)

            # Make cart inactive
            cart.deactivate()

            # Calculate orderline cost
            for orderline in order.orderline_set.all():
                orderline.calculate_cost()
        return order

    def model_to_dict(self, address):
        kwargs = address.__dict__
        for k, v in kwargs.items():
            if k.startswith('_'):
                kwargs.pop(k)

        kwargs.pop('id', None)
        return kwargs


class Order(BaseModel, DateTimeFieldMixin):
    # Cart, just for reference
    cart = models.ForeignKey('cart.Cart')
    # The user, who is creating the order
    user = models.ForeignKey('miniauth.User')
    # Address, copied from cart
    shipping_address = models.ForeignKey('Address', related_name='+')
    #: Billing Address
    billing_address = models.ForeignKey('Address', related_name='+')
    #: Subtotal of order value
    subtotal = ex_fields.FloatField(min_value=0.0, precision=2)
    #: Shipping charge of whole order
    shipping_charge = ex_fields.FloatField(min_value=0.0, precision=2)
    #: Total additional charge
    additional_charge = ex_fields.FloatField(min_value=0.0, precision=2)
    #: Cost breakup
    cost_breakup = pg_fields.JSONField()

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

    @property
    def total(self):
        return round(self.subtotal + self.shipping_charge + self.additional_charge, 2)

    def confirm(self):
        for item in self.item_set.filter(~Q(statuses__status=sts_const.CONFIRMED)):
            item.change_status(sts_const.CONFIRMED)


class OrderLine(BaseModel, DateTimeFieldMixin):
    """
    This class represents the order to be fulfilled by the seller, i.e. it has items grouped by
    seller
    """
    #: Seller user id
    user = models.ForeignKey('miniauth.User')
    #: Order id
    order = models.ForeignKey('Order')
    #: Subtotal of order value
    subtotal = ex_fields.FloatField(min_value=0.0, precision=2, default=0.0)
    #: Shipping charge of whole order
    shipping_charge = ex_fields.FloatField(min_value=0.0, precision=2, default=0.0)
    #: Total additional charge
    additional_charge = ex_fields.FloatField(min_value=0.0, precision=2, default=0.0)
    #: Cost breakup
    cost_breakup = pg_fields.JSONField(default={})

    @property
    def total(self):
        return round(self.subtotal + self.shipping_charge + self.additional_charge, 2)

    @property
    def rentalitem_set(self):
        return RentalItem.objects.filter(orderline=self)

    @property
    def purchaseitem_set(self):
        return PurchaseItem.objects.filter(orderline=self)

    def calculate_cost(self):
        q = Q(rentalitem__is_postpaid=False) | Q(rentalitem__isnull=True)
        cost = Calculator.calc_items_total(self.item_set.select_related('rentalitem').filter(q))

        self.shipping_charge = cost['shipping_charge']
        self.subtotal = cost['subtotal']
        self.additional_charge = cost['additional_charge']
        self.cost_breakup = cost['cost_breakup']

        self.save(update_fields=['cost_breakup', 'shipping_charge', 'subtotal',
                                 'additional_charge'])


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
    subtotal = ex_fields.FloatField(min_value=0.0, precision=2)
    #: Shipping charge of whole order
    shipping_charge = ex_fields.FloatField(min_value=0.0, precision=2)
    #: Total additional charge
    additional_charge = ex_fields.FloatField(min_value=0.0, precision=2)
    #: Cost breakup
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

    @property
    def total(self):
        return round(self.subtotal + self.shipping_charge + self.additional_charge, 2)

    @property
    def product(self):
        data = self.detail.copy()
        data['category_id'] = data.pop('category')
        data['location_id'] = data.pop('location')
        data['user_id'] = data.pop('user')
        data.pop('images', None)
        return Product(**data)

    def change_status(self, status, info=None, **kwargs):
        """
        Change item status

        :param status: New status
        :param comment: Comment if any
        :raise ChangeStatusError:
        """
        old_status_obj = self.current_status
        old_status = getattr(old_status_obj, 'status', None)

        signals.pre_status_change.send(instance=self, new_status=status, old_status=old_status_obj)
        L.debug('Changing status', extra={'new_status': status, 'old_status': old_status})

        # Check if new status can be changed from old status
        changeable_to = Status.CHANGEABLE_TO.get(old_status, [])

        if self.current_status and status not in changeable_to:
            L.warning('Cannot change to new status',
                      extra={'changeable_to': changeable_to, 'new_status': status, 'item': self.id})
            raise errors.ChangeStatusError(*messages.ERR_NOT_CHANGEABLE)

        # Validate and modify if new status is approved
        if status == sts_const.APPROVED:
            self.__change_status_approve()

        self.statuses.add(Status.objects.create(status=status, info=info))

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
                L.warning('Trying to add pre-occupied inventory')
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
        sts_const.PICKED_UP: [sts_const.END_CONTRACT],
        sts_const.DELIVERED: [sts_const.END_CONTRACT],
        sts_const.END_CONTRACT: [],
    }
    STATUS = [(getattr(sts_const, prop), getattr(sts_const, prop))
              for prop in dir(sts_const) if prop.startswith('_') is False]

    #: The rental item status order
    status = models.CharField(max_length=30, choices=STATUS)
    info = pg_fields.JSONField(null=True, default=None)

    Const = sts_const


class Address(AddressBase):
    pass
