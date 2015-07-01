from cart.models import Cart, RentalItem
from common.errors import ValidationError
from common.serializers import ModelSerializer
from . import messages


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart


class RentalProductSerializer(ModelSerializer):
    class Meta:
        model = RentalItem
        read_only_fields = ('shipping_cost', 'subtotal', 'is_shippable')

    def validate_product(self, value):
        product = value
        if not product.daily_price or not product.weekly_price or not product.monthly_price:
            raise ValidationError(*messages.ERR_RENT_INVALID_PRODUCT)
        return value
