from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin

from common.viewsets import GenericViewSet, NestedViewSetMixin
from models import Order, OrderLine
from order.serializers import (OrderSerializer, OrderLineSerializer, OrderLineListSerializer,
                               OrderListSerializer)


class OrderViewSet(GenericViewSet, CreateModelMixin, ListModelMixin, RetrieveModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    list_serializer_class = OrderListSerializer
    ownership_fields = ('user',)


class OrderLineViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer
    list_serializer_class = OrderLineListSerializer
    ownership_fields = ('user',)


class RentalItem(NestedViewSetMixin, GenericViewSet):
    pass
