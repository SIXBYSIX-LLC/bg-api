from common import serializers
from common.serializers import rf_serializers
from models import Product


class ProductSerializer(serializers.ModelSerializer):
    qty = rf_serializers.IntegerField(required=False)

    class Meta:
        model = Product
        read_only_fields = ('date_created_at', 'date_updated_at', 'user')

    def create(self, validated_data):
        request = self.context['request']
        validated_data['user'] = request.parent_user or request.user

        super(ProductSerializer, self).create(validated_data)

