from common import viewsets
from . import serializers, models


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.all()
