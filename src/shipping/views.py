from common.viewsets import ModelViewSet

from .models import StandardMethod
from .serializers import StandardShippingSerializer


class StandardShippingViewSet(ModelViewSet):
    queryset = StandardMethod.objects.all()
    serializer_class = StandardShippingSerializer
