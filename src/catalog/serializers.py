from common import serializers
from common.serializers import rf_serializers
from models import Product, Inventory
from static.serializers import FileRefSerializer
from usr.serializers import AddressListSerializer
from usr.models import Address
from category.serializers import CategorySerializer


class ProductSerializer(serializers.ModelSerializer):
    qty = rf_serializers.IntegerField(required=False)
    images = FileRefSerializer(many=True, read_only=True)
    review = rf_serializers.SerializerMethodField()

    class Meta:
        model = Product
        read_only_fields = ('date_created_at', 'date_updated_at', 'user')

    def create(self, validated_data):
        return Product.objects.create_product(**validated_data)

    def get_review(self, obj):
        return {
            'rating_average': getattr(obj, 'rating_average', 0.0),
            'rating_count': getattr(obj, 'rating_count', 0)
        }


class ProductListSerializer(ProductSerializer):
    category = CategorySerializer(read_only=True)
    location = AddressListSerializer(read_only=True, fields=['city', 'country', 'state',
                                                             'zip_code', 'id'])


class ProductRefSerializer(ProductSerializer):
    image = rf_serializers.ReadOnlyField()

    class Meta(ProductSerializer.Meta):
        fields = ('name', 'image', 'id')


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        write_only_fields = ('product',)
        read_only_fields = ('date_created_at', 'user')


class InventoryListSerializer(InventorySerializer):
    product = ProductRefSerializer()

    class Meta(InventorySerializer.Meta):
        write_only_fields = ()


class FacetSerializer(object):
    class LocationSerializer(serializers.Serializer):
        count = serializers.rf_serializers.IntegerField()
        location = serializers.rf_serializers.SerializerMethodField()

        class Meta:
            model = Product
            fields = ('location',)

        def get_location(self, obj):
            loc_id = obj.get('location')

            return AddressListSerializer(Address.objects.get(id=loc_id),
                                         fields=['city', 'country', 'state', 'id']).data
