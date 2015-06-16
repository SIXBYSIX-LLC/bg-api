from common.viewsets import ModelViewSet
from . import serializers
from . import models


class AddressViewSet(ModelViewSet):
    queryset = models.Address.objects.all()
    serializer_class = serializers.AddressSerializer

