from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework import status

from common.viewsets import GenericViewSet, NestedViewSetMixin
from models import Order, OrderLine, RentalItem
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
    queryset = RentalItem.objects.all()

    def action_cancel(self, request, *args, **kwargs):
        rental_item = self.get_object()
        rental_item.cancel()

        return Response(status=status.HTTP_204_NO_CONTENT)

        # @detail_route(methods=['PUT'])
        # def action_change_status(self, request, *args, **kwargs):
        # rental_item = self.get_object()
        #     rental_item.change_status()
        #
        #     return Response(status=status.HTTP_204_NO_CONTENT)
