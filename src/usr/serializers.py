import logging

from .models import Profile
from common import serializers


LOG = logging.getLogger('bgapi.' + __name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        write_only_fields = ('password',)
        read_only_fields = ('unverified_email_key', 'is_email_verified', 'is_active',
                            'is_superuser', 'is_staff', 'last_login', 'groups',
                            'user_permissions', 'is_admin', 'date_joined', 'id')

    def create(self, validated_data):
        return Profile.objects.create_user(**validated_data)


class LoginSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        exclude = ('unverified_email_key',)


class UpdateUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('fullname', 'zip_code', 'phone', 'store_name', 'timezone')
