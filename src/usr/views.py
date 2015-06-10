from common.viewsets import ModelViewSet

from . import serializers


class UserViewSet(ModelViewSet):
    queryset = serializers.Profile.objects.all()
    serializer_class = serializers.UserSerializer
