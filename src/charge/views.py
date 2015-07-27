from common.viewsets import ModelViewSet
from .serializers import SalesTaxSerializer, AdditionalChargeSerializer
from .models import SalesTax, AdditionalCharge


class SalesTaxViewSet(ModelViewSet):
    serializer_class = SalesTaxSerializer
    queryset = SalesTax.objects.all()


class AdditionalChargeViewSet(ModelViewSet):
    serializer_class = AdditionalChargeSerializer
    queryset = AdditionalCharge.objects.all()
    ownership_fields = ('user',)
