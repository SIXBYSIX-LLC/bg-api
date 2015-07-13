from cart.models import Cart, RentalItem, Item, PurchaseItem
from catalog.serializers import ProductRefSerializer
from common.errors import ValidationError
from common.serializers import ModelSerializer
from . import messages


class ItemSerializer(ModelSerializer):
    """
    Base class for Rental / Purchase serializer
    """
    class Meta:
        model = Item
        read_only_fields = ('shipping_cost', 'subtotal', 'is_shippable', 'cost_breakup')

    def create(self, validated_data):
        instance = super(ItemSerializer, self).create(validated_data)
        instance.cart.calculate_cost()

        return instance

    def update(self, instance, validated_data):
        # Prevent product attribute from updating
        validated_data.pop('product', None)

        instance = super(ItemSerializer, self).update(instance, validated_data)
        instance.cart.calculate_cost()

        return instance


class RentalProductSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        model = RentalItem

    def validate_product(self, value):
        product = value
        if not product.daily_price or not product.weekly_price or not product.monthly_price:
            raise ValidationError(*messages.ERR_RENT_INVALID_PRODUCT)
        return value

    def validate(self, data):
        date_start = data.get('date_start')
        date_end = data.get('date_end')
        product = data.get('product') or self.instance

        if date_start and date_end:
            min_contract_period = product.user.profile.settings['minimum_contract_period']
            if (date_end - date_start).days < min_contract_period:
                raise ValidationError(*messages.ERR_INVALID_END_DATE)

        return data


class RentalProductListSerializer(RentalProductSerializer):
    product = ProductRefSerializer()


class PurchaseProductSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        model = PurchaseItem

    def validate_product(self, value):
        product = value
        if not product.sell_price:
            raise ValidationError(*messages.ERR_PURCHASE_INVALID_PRODUCT)
        return value


class PurchaseProductListSerializer(PurchaseProductSerializer):
    product = ProductRefSerializer()


class CartSerializer(ModelSerializer):
    rental_products = RentalProductListSerializer(source='rentalitem_set', many=True)
    purchase_products = PurchaseProductListSerializer(source='purchaseitem_set', many=True)

    class Meta:
        model = Cart
        read_only_fields = ('rental_products', 'user', 'is_active', 'total', 'purchase_products')

    def update(self, instance, validated_data):
        instance = super(CartSerializer, self).update(instance, validated_data)
        instance.calculate_cost()

        return instance
