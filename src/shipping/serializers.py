from common.serializers import ModelSerializer
from .models import StandardMethod


class StandardShippingSerializer(ModelSerializer):
    class Meta:
        model = StandardMethod

