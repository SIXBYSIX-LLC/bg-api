from catalog.models import Inventory
from common.serializers import ModelSerializer, rf_serializers, Serializer
from .models import Order, OrderLine, Item, RentalItem
from order import messages
from common.errors import OrderError
from usr.serializers import UserRefSerializer
from usr.serializers import AddressListSerializer

from catalog.serializers import ProductRefSerializer


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
                      'images')

    detail = DetailSerializer()

    class Meta(ItemSerializer.Meta):
        depth = 0


class OrderSerializer(ModelSerializer):
    items = ItemSerializer(many=True, source='item_set')
    country = AddressListSerializer.CountryRefSerializer(read_only=True)
    state = AddressListSerializer.RegionRefSerializer(read_only=True)
    city = AddressListSerializer.CityRefSerializer(read_only=True)

    class Meta:
        model = Order
        write_only_fields = ('cart',)
        read_only_fields = ('id', 'user', 'address', 'country', 'state', 'city',
                            'zip_code', 'total')

    def create(self, validated_data):
        return Order.objects.create_order(validated_data.get('cart'))

    def validate_cart(self, value):
        cart = value
        if self.context['request'].user != cart.user:
            raise OrderError(*messages.ERR_INVALID_CART_USER)

        return value


class OrderListSerializer(OrderSerializer):
    items = ItemListSerializer(many=True, source='rentalitem_set')


class OrderLineSerializer(ModelSerializer):
    class OrderRefSerializer(OrderSerializer):
        user = UserRefSerializer(source='user.profile')

        class Meta:
            model = Order
            exclude = ('cart', 'items', 'total')

    items = ItemSerializer(many=True, source='item_set')
    order = OrderRefSerializer()

    class Meta:
        model = OrderLine


class OrderLineListSerializer(OrderLineSerializer):
    items = ItemListSerializer(many=True, source='item_set')


class ChangeStatusSerializer(Serializer):
    status = rf_serializers.CharField()
    comment = rf_serializers.CharField(required=False)


class AddInventorySerializer(Serializer):
    inventories = rf_serializers.PrimaryKeyRelatedField(many=True,
                                                        queryset=Inventory.objects.all())

    def create(self, validated_data):
        item = self.context['item']

        item.inventories.update(is_active=True)
        item.inventories.clear()

        item.add_inventories(*validated_data.get('inventories'))
        return item
