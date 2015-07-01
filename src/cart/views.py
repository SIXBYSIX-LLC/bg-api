from rest_framework.decorators import list_route
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response

from cart.models import RentalItem
from cart.serializers import CartSerializer, RentalProductSerializer
from common.viewsets import GenericViewSet, NestedViewSetMixin
from .models import Cart


class CartViewSet(GenericViewSet, UpdateModelMixin):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @list_route(methods=['GET'])
    def current(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(is_active=True, user=request.user)
        serializer = CartSerializer(cart)

        return Response(serializer.data)


class RentalItemViewSet(NestedViewSetMixin, GenericViewSet, CreateModelMixin, DestroyModelMixin):
    serializer_class = RentalProductSerializer
    queryset = RentalItem.objects.all()

    def create(self, request, *args, **kwargs):
        request.data.update(**self.get_parents_query_dict())

        return super(RentalItemViewSet, self).create(request, *args, **kwargs)
