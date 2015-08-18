from .models import AdditionalCharge
from common.serializers import ModelSerializer


class AdditionalChargeSerializer(ModelSerializer):
    class Meta:
        model = AdditionalCharge
        read_only_fields = ('user',)
