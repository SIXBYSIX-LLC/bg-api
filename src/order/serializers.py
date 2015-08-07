from rest_framework.exceptions import PermissionDenied

from catalog.models import Inventory
from common.serializers import ModelSerializer, rf_serializers, Serializer
from .models import Order, OrderLine, Item, RentalItem
from order import messages
from common.errors import OrderError
from usr.serializers import UserRefSerializer
from catalog.serializers import ProductRefSerializer
from constants import Status as sts_const


class ItemSerializer(ModelSerializer):
    class RentalItemSerializer(ModelSerializer):
        class Meta:
            model = RentalItem
            fields = ('date_start', 'date_end', 'is_postpaid')

    current_status = rf_serializers.CharField(source='current_status.status')
    user = UserRefSerializer(source='user.profile')
    rent_details = RentalItemSerializer(source='rentalitem', read_only=True)

    class Meta:
        model = Item
        exclude = ('order', 'orderline', 'inventories', 'statuses')
        depth = 2


class ItemListSerializer(ItemSerializer):
    class DetailSerializer(ProductRefSerializer):
        class Meta(ProductRefSerializer.Meta):
            fields = ('id', 'name', 'daily_price', 'sell_price', 'weekly_price', 'monthly_price',
                      'image')

        def get_image(self, obj):
            if obj['images']:
                return obj['images'][0]

    detail = DetailSerializer()

    class Meta(ItemSerializer.Meta):
        depth = 0
        exclude = ItemSerializer.Meta.exclude + ('cost_breakup',)


class OrderSerializer(ModelSerializer):
    items = ItemSerializer(many=True, source='item_set')
    total = rf_serializers.FloatField(read_only=True)

    class Meta:
        model = Order
        write_only_fields = ('cart',)
        read_only_fields = ('id', 'billing_address', 'shipping_address', 'total', 'user',
                            'subtotal', 'shipping_charge', 'additional_charge', 'cost_breakup')

    def create(self, validated_data):
        return Order.objects.create_order(validated_data.get('cart'))

    def validate_cart(self, value):
        cart = value
        if self.context['request'].user != cart.user:
            raise OrderError(*messages.ERR_INVALID_CART_USER)

        return value


class OrderListSerializer(OrderSerializer):
    items = ItemListSerializer(many=True, source='item_set')

    class Meta(OrderSerializer.Meta):
        exclude = ('shipping_address', 'billing_address', 'cost_breakup')


class OrderLineSerializer(ModelSerializer):
    class OrderRefSerializer(OrderSerializer):
        user = UserRefSerializer(source='user.profile')

        class Meta:
            model = Order
            exclude = ('cart', 'items', 'total')

    items = ItemSerializer(many=True, source='item_set')
    order = OrderRefSerializer()
    total = rf_serializers.FloatField(read_only=True)

    class Meta:
        model = OrderLine


class OrderLineListSerializer(OrderLineSerializer):
    class OrderRefSerializer(OrderLineSerializer.OrderRefSerializer):
        user = UserRefSerializer(source='user.profile')

        class Meta(OrderLineSerializer.OrderRefSerializer.Meta):
            model = Order
            exclude = OrderLineSerializer.OrderRefSerializer.Meta.exclude + (
                'shipping_address', 'billing_address', 'cost_breakup'
            )

    order = OrderRefSerializer()
    items = ItemListSerializer(many=True, source='item_set')


class ChangeStatusSerializer(Serializer):
    status = rf_serializers.CharField()
    info = rf_serializers.DictField(required=False)

    def validate(self, validated_data):
        item = self.context['item']
        request = self.context['request']
        user = request.parent_user or request.user

        # Ensure that order user can only change status to cancel and delivered status
        if item.order.user == user:
            if validated_data['status'] not in [sts_const.CANCEL, sts_const.DELIVERED]:
                raise PermissionDenied

        return validated_data


class AddInventorySerializer(Serializer):
    inventories = rf_serializers.PrimaryKeyRelatedField(many=True,
                                                        queryset=Inventory.objects.all())

    def create(self, validated_data):
        item = self.context['item']

        item.inventories.update(is_active=True)
        item.inventories.clear()

        item.add_inventories(*validated_data.get('inventories'))
        return item
