from common.viewsets import ModelViewSet
from .serializers import SalesTaxSerializers
from .models import SalesTax


class SalesTaxViewSet(ModelViewSet):
    serializer_class = SalesTaxSerializers
    queryset = SalesTax.objects.all()
