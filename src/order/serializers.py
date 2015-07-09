from common.serializers import ModelSerializer
from .models import Order, RentalItem, OrderLine
from order import messages
from order.errors import OrderError
from usr.serializers import UserRefSerializer
from usr.serializers import AddressListSerializer

from catalog.serializers import ProductRefSerializer


class RentalItemSerializer(ModelSerializer):
    user = UserRefSerializer(source='user.profile')

    class Meta:
        model = RentalItem
        exclude = ('order', 'orderline', 'inventory')


class RentalItemListSerializer(RentalItemSerializer):
    class DetailSerializer(ProductRefSerializer):
        class Meta(ProductRefSerializer.Meta):
            fields = ('id', 'name', 'daily_price', 'sell_price', 'weekly_price', 'monthly_price',
                      'images')

    detail = DetailSerializer()


class OrderSerializer(ModelSerializer):
    rental_items = RentalItemSerializer(many=True, source='rentalitem_set')
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


class OrderLineSerializer(ModelSerializer):
    class OrderRefSerializer(OrderSerializer):
        user = UserRefSerializer(source='user.profile')

        class Meta:
            model = Order
            exclude = ('cart', 'rental_items')

    rental_items = RentalItemSerializer(many=True, source='rentalitem_set')
    order = OrderRefSerializer()

    class Meta:
        model = OrderLine


class OrderLineListSerializer(OrderLineSerializer):
    rental_items = RentalItemListSerializer(many=True, source='rentalitem_set')
