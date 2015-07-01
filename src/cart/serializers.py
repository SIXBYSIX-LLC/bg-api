from cart.models import Cart, RentalItem
from common.serializers import ModelSerializer


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart


class RentalProductSerializer(ModelSerializer):
    class Meta:
        model = RentalItem
        exclude = ('shipping_cost', 'subtotal')
