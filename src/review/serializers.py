from common.serializers import ModelSerializer
from .models import OrderItem
from usr.serializers import UserRefSerializer


class OrderItemReviewSerializer(ModelSerializer):
    class Meta:
        model = OrderItem

    def create(self, validated_data):
        return OrderItem.objects.create_review(**validated_data)


class OrderItemViewSerializer(OrderItemReviewSerializer):
    user = UserRefSerializer(source='user.profile')
    to_user = UserRefSerializer(source='to_user.profile')
