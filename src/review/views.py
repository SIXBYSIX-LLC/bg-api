from common.viewsets import ModelViewSet
from .models import OrderItem
from review.serializers import OrderItemViewSerializer
from .serializers import OrderItemReviewSerializer


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemReviewSerializer
    view_serializer_class = list_serializer_class = OrderItemViewSerializer

    ownership_fields = ('user',)
    filter_fields = ('reviewer', 'product')
    skip_owner_filter = True

