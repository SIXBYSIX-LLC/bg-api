from django.db.models import Count, Case, When, Value

from common import viewsets
from . import serializers, models


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.all()

    def get_queryset(self):
        qs = super(ProductViewSet, self).get_queryset()
        qs = qs.annotate(qty=Count(Case(When(inventory__is_active=True, then=Value(1)))))
        return qs


class InventoryViewSet(viewsets.NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = serializers.InventorySerializer
    queryset = models.Inventory.objects.all()

