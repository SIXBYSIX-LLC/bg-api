from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin

from common.viewsets import GenericViewSet, NestedViewSetMixin
from .models import Invoice, InvoiceLine, Item
from .serializers import (InvoiceSerializer, InvoiceRetrieveSerializer, InvoiceLineSerializer,
                          ItemSerializer)


class InvoiceViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = Invoice.approved.all()
    serializer_class = InvoiceSerializer
    retrieve_serializer_class = InvoiceRetrieveSerializer
    ownership_fields = ('user',)
    filter_fields = ('order',)


class InvoiceLineViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin):
    queryset = InvoiceLine.objects.all()
    serializer_class = InvoiceLineSerializer
    ownership_fields = ('user',)


class ItemViewSet(NestedViewSetMixin, GenericViewSet, ListModelMixin, UpdateModelMixin):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    ownership_fields = ('user',)
