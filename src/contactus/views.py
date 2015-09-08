from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin

from common.viewsets import GenericViewSet
from .models import ContactUs
from .serializers import ContactUsSerializer


class ContactUsViewSet(GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
