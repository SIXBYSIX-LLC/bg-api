from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin

from common.viewsets import GenericViewSet
from models import Order
from order.serializers import OrderSerializer


class OrderViewSet(GenericViewSet, CreateModelMixin, ListModelMixin, RetrieveModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    ownershipe_fields = ('user',)
