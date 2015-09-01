from common.serializers import ModelSerializer
from .models import OrderItem


class OrderItemReviewSerializer(ModelSerializer):
    class Meta:
        model = OrderItem

    def create(self, validated_data):
        return OrderItem.objects.create_review(**validated_data)
