from common.viewsets import ModelViewSet

from . import serializers


class UserViewSet(ModelViewSet):
    queryset = serializers.Profile.objects.all()
    serializer_class = serializers.UserSerializer
    update_serializer_class = serializers.UpdateUserSerializer
    partial_update_serializer_class = update_serializer_class
