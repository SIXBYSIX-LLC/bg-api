from common.serializers import ModelSerializer, rf_serializers, Serializer
from .models import Order, RentalItem, OrderLine, PurchaseItem
from order import messages
from order.errors import OrderError
from usr.serializers import UserRefSerializer
from usr.serializers import AddressListSerializer

from catalog.serializers import ProductRefSerializer


class ItemSerializer(ModelSerializer):
    current_status = rf_serializers.CharField(source='current_status.status')
    user = UserRefSerializer(source='user.profile')

    class Meta:
        exclude = ('order', 'orderline', 'inventory')
        depth = 1


class ItemListSerializer(ItemSerializer):
    class DetailSerializer(ProductRefSerializer):
        class Meta(ProductRefSerializer.Meta):
            fields = ('id', 'name', 'daily_price', 'sell_price', 'weekly_price', 'monthly_price',
                      'images')

    detail = DetailSerializer()

    class Meta(ItemSerializer.Meta):
        depth = 0


class RentalItemSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        model = RentalItem


class RentalItemListSerializer(RentalItemSerializer, ItemListSerializer):
    class Meta(RentalItemSerializer.Meta, ItemListSerializer.Meta):
        pass


class PurchaseItemSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        model = PurchaseItem


class PurchaseItemListSerializer(ItemListSerializer, PurchaseItemSerializer):
    class Meta(PurchaseItemSerializer.Meta, ItemListSerializer.Meta):
        pass


class OrderSerializer(ModelSerializer):
    rental_items = RentalItemSerializer(many=True, source='rentalitem_set')
    purchase_items = PurchaseItemSerializer(many=True, source='purchaseitem_set')
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
    rental_items = RentalItemListSerializer(many=True, source='rentalitem_set')
    purchase_items = PurchaseItemListSerializer(many=True, source='purchaseitem_set')


class OrderLineSerializer(ModelSerializer):
    class OrderRefSerializer(OrderSerializer):
        user = UserRefSerializer(source='user.profile')

        class Meta:
            model = Order
            exclude = ('cart', 'rental_items')

    rental_items = RentalItemSerializer(many=True, source='rentalitem_set')
    purchase_items = PurchaseItemSerializer(many=True, source='purchaseitem_set')
    order = OrderRefSerializer()

    class Meta:
        model = OrderLine


class OrderLineListSerializer(OrderLineSerializer):
    rental_items = RentalItemListSerializer(many=True, source='rentalitem_set')
    purchase_items = PurchaseItemListSerializer(many=True, source='purchaseitem_set')


class ChangeStatusSerializer(Serializer):
    status = rf_serializers.CharField()
    comment = rf_serializers.CharField(required=False)
