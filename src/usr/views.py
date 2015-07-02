from rest_framework.response import Response
from rest_framework.decorators import detail_route, api_view, permission_classes
from rest_framework import status, mixins
from rest_framework.permissions import AllowAny

from common.viewsets import ModelViewSet, NestedViewSetMixin, GenericViewSet
from common.permissions import CustomActionPermissions
from . import serializers
from .models import Profile, Address
from usr.serializers import SettingSerializer


class UserViewSet(ModelViewSet):
    queryset = serializers.Profile.objects.all()
    serializer_class = serializers.UserSerializer
    update_serializer_class = serializers.UpdateUserSerializer
    partial_update_serializer_class = update_serializer_class

    ownership_fields = ('user',)

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

    @detail_route(methods=['PATCH', 'GET'])
    def setting(self, request, *args, **kwargs):
        user = self.get_object()
        if request.method == 'PATCH':
            serializer = SettingSerializer(data=request.data, partial=True)
            serializer.is_valid(True)

            user.settings.update(**serializer.data)
            user.save(update_fields=['settings'])

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = SettingSerializer(user.settings)
            return Response(serializer.data, status=status.HTTP_200_OK)

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


class AddressViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = serializers.AddressSerializer
    list_serializer_class = retrieve_serializer_class = serializers.AddressListSerializer
    filter_fields = ('kind',)


class FavoriteProductViewSet(NestedViewSetMixin, GenericViewSet, mixins.ListModelMixin,
                             mixins.CreateModelMixin, mixins.DestroyModelMixin):
    """
    This is a special class. The actual favorite model doesn't exist but ManyToMany related in
    Profile class. Hence get_queryset() has to be overridden.

    Moreover, It inherits all Profile model permission so we have to give user to delete object
    permission to give ability to delete favorite object
    """
    from catalog.serializers import ProductRefSerializer

    queryset = Profile.objects.all()
    serializer_class = ProductRefSerializer

    def create(self, request, *args, **kwargs):
        user = request.user.profile
        user.favorite_products.add(request.data.get('id'))

        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        user = request.user.profile
        user.favorite_products.remove(kwargs.get('pk'))

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        # to adjust the permission
        if self.request.method == 'GET':
            return self.request.user.profile.favorite_products.all()
        return self.queryset
