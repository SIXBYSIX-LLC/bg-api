from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response

from cart.models import RentalItem, PurchaseItem
from cart.serializers import CartSerializer, RentalProductSerializer, PurchaseProductSerializer
from common.viewsets import GenericViewSet, NestedViewSetMixin
from .models import Cart
from order.models import Order
from invoice.models import Invoice


class CartViewSet(GenericViewSet, UpdateModelMixin):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @list_route(methods=['GET'])
    def current(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(is_active=True, user=request.user)
        serializer = CartSerializer(cart)

        return Response(serializer.data)

    @list_route(methods=['PUT'])
    def checkout(self):
        cart = self.get_object()
        order = Order.objects.create_order(cart)
        invoice = Invoice.objects.create_from_order(order)

        data = {'invoice': invoice.id, 'payable_amount': invoice.total, 'order': order.id}
        return Response(data)


class RentalItemViewSet(NestedViewSetMixin, GenericViewSet, CreateModelMixin, DestroyModelMixin,
                        UpdateModelMixin):
    serializer_class = RentalProductSerializer
    queryset = RentalItem.objects.all()

    def create(self, request, *args, **kwargs):
        request.data.update(**self.get_parents_query_dict())

        super(RentalItemViewSet, self).create(request, *args, **kwargs)

        cart = self.get_parent_object()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        request.data.update(**self.get_parents_query_dict())

        super(RentalItemViewSet, self).update(request, *args, **kwargs)

        cart = self.get_parent_object()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        request.data.update(**self.get_parents_query_dict())

        super(RentalItemViewSet, self).partial_update(request, *args, **kwargs)

        cart = self.get_parent_object()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        super(RentalItemViewSet, self).destroy(request, *args, **kwargs)

        cart = self.get_parent_object()
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class PurchaseItemViewSet(RentalItemViewSet):
    queryset = PurchaseItem.objects.all()
    serializer_class = PurchaseProductSerializer
