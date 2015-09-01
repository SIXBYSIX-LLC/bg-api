from common.viewsets import ModelViewSet
from .models import OrderItem
from .serializers import OrderItemReviewSerializer


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemReviewSerializer

    ownership_fields = ('user',)
    filter_fields = ('reviewer', 'product')

