from common import serializers
from common.serializers import rf_serializers
from models import Product, Inventory
from static.serializers import FileRefSerializer
from usr.serializers import AddressListSerializer
from usr.models import Address


class ProductSerializer(serializers.ModelSerializer):
    qty = rf_serializers.IntegerField(required=False)
    images = FileRefSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        read_only_fields = ('date_created_at', 'date_updated_at', 'user')

    def create(self, validated_data):
        return Product.objects.create_product(**validated_data)


class ProductListSerializer(ProductSerializer):
    location = AddressListSerializer(read_only=True, fields=['city', 'country', 'state',
                                                             'zip_code', 'id'])


class ProductRefSerializer(ProductSerializer):
    image = rf_serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ('name', 'image', 'id')

    def get_image(self, obj):
        img = obj.images.first()
        return img.url if img else img


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        write_only_fields = ('product',)
        read_only_fields = ('date_created_at', 'user')


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
                                         fields=['city', 'country', 'state']).data
