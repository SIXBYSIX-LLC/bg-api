from .models import SalesTax
from common.serializers import ModelSerializer


class SalesTaxSerializers(ModelSerializer):
    class Meta:
        model = SalesTax
