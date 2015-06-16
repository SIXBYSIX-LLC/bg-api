from cities.models import PostalCode

from common import serializers, errors
from .models import Address
from . import messages


class AddressSerializer(serializers.GeoModelSerializer):
    class Meta:
        model = Address
        read_only_fields = ('user',)

    def create(self, validated_data):
        user = self.context['request'].user
        if user.profile.user:
            user = user.profile.user

        validated_data['user'] = user

        return Address.objects.create(**validated_data)

    def validate(self, attrs):
        zip_count = PostalCode.objects.filter(code=attrs.get('zip_code'),
                                              country=attrs.get('country')).count()
        if zip_count == 0:
            raise errors.ValidationError(*messages.ERR_INVALID_ZIP_CODE)

        return attrs
