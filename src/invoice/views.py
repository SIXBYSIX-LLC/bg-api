from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework import decorators, status

from common.viewsets import GenericViewSet, NestedViewSetMixin
from common.permissions import CustomActionPermissions, IsOwnerPermissions
from .models import Invoice, InvoiceLine, Item
from .serializers import (InvoiceSerializer, InvoiceRetrieveSerializer, InvoiceLineSerializer,
                          ItemSerializer, InvoicePaymentSerializer)
from transaction.models import Transaction
from transaction.serializer import TransactionRefSerializer


class InvoiceViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = Invoice.approved.all()
    serializer_class = InvoiceSerializer
    retrieve_serializer_class = InvoiceRetrieveSerializer
    ownership_fields = ('user',)
    filter_fields = ('order',)

    @decorators.detail_route(methods=['POST'], permission_classes=(IsOwnerPermissions,
                                                                   CustomActionPermissions,))
    def action_pay(self, request, *args, **kwargs):
        invoice = self.get_object()
        serializer = InvoicePaymentSerializer(data=request.data)
        serializer.is_valid(True)

        redirect_url, transaction = Transaction.objects.pay_invoice(
            invoice=invoice, **serializer.data
        )
        t_serializer = TransactionRefSerializer(transaction)

        return Response({'redirect_url': redirect_url, 'transaction': t_serializer.data})


class InvoiceLineViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin):
    queryset = InvoiceLine.objects.all()
    serializer_class = InvoiceLineSerializer
    ownership_fields = ('user',)

    @decorators.detail_route(methods=['PUT'], permission_classes=(IsOwnerPermissions,
                                                                  CustomActionPermissions,))
    def action_approve(self, request, *args, **kwargs):
        invoiceline = self.get_object()
        invoiceline.approve()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemViewSet(NestedViewSetMixin, GenericViewSet, ListModelMixin, UpdateModelMixin):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    ownership_fields = ('user',)
