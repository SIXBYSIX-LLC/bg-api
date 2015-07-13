from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import detail_route

from common.viewsets import GenericViewSet, NestedViewSetMixin
from models import Order, OrderLine, RentalItem
from order.serializers import (OrderSerializer, OrderLineSerializer, OrderLineListSerializer,
                               OrderListSerializer, ChangeStatusSerializer)


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


class Item(NestedViewSetMixin, GenericViewSet):
    queryset = RentalItem.objects.all()

    @detail_route(methods=['PUT'])
    def action_change_status(self, request, *args, **kwargs):
        item = self.get_object()

        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(True)

        item.change_status(serializer.data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['PUT'])
    def inventories(self, request, *args, **kwargs):
        item = self.get_object()

        item.add_inventories()
