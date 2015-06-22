from common import serializers
from common.serializers import rf_serializers
from models import Product, Inventory


class ProductSerializer(serializers.ModelSerializer):
    qty = rf_serializers.IntegerField(required=False)

    class Meta:
        model = Product
        read_only_fields = ('date_created_at', 'date_updated_at', 'user')

    def create(self, validated_data):
        request = self.context['request']
        validated_data['user'] = request.parent_user or request.user

        return Product.objects.create_product(**validated_data)


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        write_only_fields = ('product',)
        read_only_fields = ('date_created_at',)


