"""
===========
Serializers
===========
"""
from django.utils import timezone
from rest_framework.validators import UniqueTogetherValidator

from cart.models import Cart, RentalItem, Item, PurchaseItem
from catalog.serializers import ProductRefSerializer
from common.errors import ValidationError
from common.serializers import ModelSerializer, rf_serializers
from . import messages


class ItemSerializer(ModelSerializer):
    """
    Base class for Rental / Purchase serializer
    """
    class Meta:
        model = Item
        read_only_fields = ['shipping_charge', 'subtotal', 'is_shippable', 'cost_breakup']

    def create(self, validated_data):
        """
        Override to call ``cart.calculate_cost()``
        """
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
        read_only_fields = ItemSerializer.Meta.read_only_fields + ['is_postpaid']
        validators = [
            UniqueTogetherValidator(
                queryset=RentalItem.objects.all(),
                fields=('cart', 'product', 'date_start', 'date_end'),
                message='Product is already in your cart'
            )
        ]

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
            min_contract_period = product.user.profile.settings.get('minimum_contract_period', 1)
            if (date_end - date_start).days < min_contract_period:
                raise ValidationError(*messages.ERR_INVALID_END_DATE)

        if date_start:
            notice_period = product.user.profile.settings.get('minimum_rent_notice_period', 0)
            if (date_start - timezone.now()).days < notice_period:
                raise ValidationError(messages.ERR_INVALID_START_DATE[0] % notice_period,
                                      messages.ERR_INVALID_START_DATE[1])

        return data


class RentalProductListSerializer(RentalProductSerializer):
    product = ProductRefSerializer()


class PurchaseProductSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        model = PurchaseItem
        validators = [
            UniqueTogetherValidator(
                queryset=PurchaseItem.objects.all(),
                fields=('cart', 'product'),
                message='Product is already in your cart'
            )
        ]

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
    total = rf_serializers.FloatField(read_only=True)

    class Meta:
        model = Cart
        read_only_fields = ('rental_products', 'user', 'is_active', 'total', 'purchase_products',
                            'cost_breakup')

    def update(self, instance, validated_data):
        instance = super(CartSerializer, self).update(instance, validated_data)
        instance.calculate_cost()

        return instance
