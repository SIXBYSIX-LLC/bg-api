from rest_framework.response import Response
from rest_framework.decorators import detail_route, api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny

from common.viewsets import ModelViewSet
from common.permissions import CustomActionPermissions
from . import serializers
from .models import Profile


class UserViewSet(ModelViewSet):
    queryset = serializers.Profile.objects.all()
    serializer_class = serializers.UserSerializer
    update_serializer_class = serializers.UpdateUserSerializer
    partial_update_serializer_class = update_serializer_class

    @detail_route(methods=['POST'])
    def action_change_password(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = serializers.ChangePasswordSerializer(data=request.data)
        serializer.is_valid(True)

        user.change_password(**serializer.data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['POST'])
    def action_resend_email_verification(self, request, *args, **kwargs):
        user = self.get_object()
        user.send_email_verification()

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'PUT'])
@permission_classes((AllowAny,))
def password_reset(request, *args, **kwargs):
    if request.method == 'POST':
        Profile.objects.generate_password_reset_key(request.data.get('email'))
    else:
        serializer = serializers.ResetPasswordSerializer(data=request.data)
        serializer.is_valid(True)
        Profile.objects.reset_password(**serializer.data)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes((AllowAny,))
def verify_email(request, *args, **kwargs):
    Profile.objects.verify_email(request.data.get('key'))

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes((CustomActionPermissions,))
def resend_email_verification(request, *args, **kwargs):
    """
    This API is intended for Admins/Staff
    """
    Profile.objects.resend_email_verification(email=request.data.get('email'))

