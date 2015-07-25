import logging

from cities.models import PostalCode, Country, City, Region

from .models import Profile, Address
from common import serializers
from common.serializers import rf_serializers
from group.serializers import GroupRefSerializer
from static.serializers import FileRefSerializer

LOG = logging.getLogger('bgapi.' + __name__)


class SettingSerializer(serializers.Serializer):
    daily_price_till_days = rf_serializers.IntegerField(min_value=2, required=False)
    weekly_price_till_days = rf_serializers.IntegerField(min_value=7, required=False)
    minimum_contract_period = rf_serializers.IntegerField(min_value=2, required=False)


class UserSerializer(serializers.ModelSerializer):
    groups = GroupRefSerializer(read_only=True, many=True)
    user = rf_serializers.PrimaryKeyRelatedField(read_only=True)
    credit_form = FileRefSerializer(read_only=True)

    class Meta:
        model = Profile
        write_only_fields = ('password',)
        read_only_fields = ('is_email_verified', 'is_active', 'is_superuser', 'is_staff',
                            'last_login', 'groups', 'user_permissions', 'date_joined', 'id',
                            'user', 'settings', 'credit_form')
        exclude = ('unverified_email_key', 'is_admin', 'password_reset_key')
        depth = 1

    def create(self, validated_data):
        return Profile.objects.create_user(**validated_data)


class UserRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('fullname', 'id')


class LoginSerializer(UserSerializer):
    pass


class UpdateUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('fullname', 'zip_code', 'phone', 'store_name', 'timezone')
        exclude = ()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = rf_serializers.CharField(max_length=128, min_length=3, required=True)
    new_password = rf_serializers.CharField(max_length=128, min_length=3, required=True)


class ResetPasswordSerializer(serializers.Serializer):
    email = rf_serializers.EmailField(required=True)
    reset_key = rf_serializers.UUIDField(required=True)
    new_password = rf_serializers.CharField(max_length=128, min_length=3, required=True)


class AddressSerializer(serializers.GeoModelSerializer):
    class Meta:
        model = Address
        exclude = ('user',)

    def validate(self, attrs):
        zip_count = PostalCode.objects.filter(code=attrs.get('zip_code'),
                                              country=attrs.get('country')).count()
        # if zip_count == 0:
        # raise errors.ValidationError(*messages.ERR_INVALID_ZIP_CODE)

        return attrs


class AddressListSerializer(AddressSerializer):
    class CountryRefSerializer(serializers.ModelSerializer):
        class Meta:
            model = Country
            fields = ('name', 'id')

    class RegionRefSerializer(serializers.ModelSerializer):
        class Meta:
            model = Region
            fields = ('name', 'id')

    class CityRefSerializer(serializers.ModelSerializer):
        class Meta:
            model = City
            fields = ('name', 'id')

    country = CountryRefSerializer(read_only=True)
    state = RegionRefSerializer(read_only=True)
    city = CityRefSerializer(read_only=True)

    class Meta(AddressSerializer.Meta):
        read_only_fields = ()
