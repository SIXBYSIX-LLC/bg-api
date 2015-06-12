import logging

from django.contrib.auth.models import AnonymousUser

from .models import Profile
from common import serializers
from common.serializers import rf_serializers

LOG = logging.getLogger('bgapi.' + __name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        write_only_fields = ('password',)
        read_only_fields = ('unverified_email_key', 'is_email_verified', 'is_active',
                            'is_superuser', 'is_staff', 'last_login', 'groups',
                            'user_permissions', 'is_admin', 'date_joined', 'id', 'user')
        depth = 1

    def create(self, validated_data):
        user = self.context.get('request').user
        if isinstance(user, AnonymousUser):
            user = None
        return Profile.objects.create_user(user=user, **validated_data)


class LoginSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        exclude = ('unverified_email_key',)


class UpdateUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('fullname', 'zip_code', 'phone', 'store_name', 'timezone')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = rf_serializers.CharField(max_length=128, min_length=3, required=True)
    new_password = rf_serializers.CharField(max_length=128, min_length=3, required=True)


class ResetPasswordSerializer(serializers.Serializer):
    email = rf_serializers.EmailField(required=True)
    reset_key = rf_serializers.UUIDField(required=True)
    new_password = rf_serializers.CharField(max_length=128, min_length=3, required=True)
