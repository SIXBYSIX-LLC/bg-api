from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework import status

from common.viewsets import ModelViewSet
from . import serializers


class UserViewSet(ModelViewSet):
    queryset = serializers.Profile.objects.all()
    serializer_class = serializers.UserSerializer
    update_serializer_class = serializers.UpdateUserSerializer
    partial_update_serializer_class = update_serializer_class

    @detail_route(methods=['PUT'])
    def password(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = serializers.ChangePasswordSerializer(data=request.data)
        serializer.is_valid(True)

        user.change_password(**serializer.data)

        return Response(status=status.HTTP_204_NO_CONTENT)
