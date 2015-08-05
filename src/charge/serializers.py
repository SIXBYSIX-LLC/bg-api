from .models import SalesTax, AdditionalCharge
from common.serializers import ModelSerializer


class SalesTaxSerializer(ModelSerializer):
    class Meta:
        model = SalesTax


class AdditionalChargeSerializer(ModelSerializer):
    class Meta:
        model = AdditionalCharge
        read_only_fields = ('user',)
