from common.serializers import ModelSerializer
from .models import Order, RentalItem
from order import messages
from order.errors import OrderError


class RentalItemSerializer(ModelSerializer):
    class Meta:
        model = RentalItem


class OrderSerializer(ModelSerializer):
    rental_items = RentalItemSerializer(many=True, source='rentalitem_set')

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
