from common.viewsets import ModelViewSet
from .serializers import AdditionalChargeSerializer
from .models import AdditionalCharge


class AdditionalChargeViewSet(ModelViewSet):
    serializer_class = AdditionalChargeSerializer
    queryset = AdditionalCharge.objects.all()
    ownership_fields = ('user',)
