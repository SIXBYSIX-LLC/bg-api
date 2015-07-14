from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import detail_route

from common.viewsets import GenericViewSet, NestedViewSetMixin
from models import Order, OrderLine, Item
from order.serializers import (OrderSerializer, OrderLineSerializer, OrderLineListSerializer,
                               OrderListSerializer, ChangeStatusSerializer, AddInventorySerializer)


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


class ItemViewSet(NestedViewSetMixin, GenericViewSet):
    queryset = Item.objects.all()

    @detail_route(methods=['PUT'])
    def action_change_status(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = ChangeStatusSerializer(data=request.data, context={'request': request,
                                                                        'item': item})
        serializer.is_valid(True)

        item.change_status(**serializer.data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['PUT'])
    def inventories(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = AddInventorySerializer(data=request.data, context={'item': item})
        serializer.is_valid(True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
