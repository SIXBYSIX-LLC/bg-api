from common import serializers
from common.serializers import rf_serializers
from models import Product, Inventory
from static.serializers import FileRefSerializer


class ProductSerializer(serializers.ModelSerializer):
    qty = rf_serializers.IntegerField(required=False)
    images = FileRefSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        read_only_fields = ('date_created_at', 'date_updated_at', 'user')

    def create(self, validated_data):
        return Product.objects.create_product(**validated_data)


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        write_only_fields = ('product',)
        read_only_fields = ('date_created_at', 'user')


