from django.utils import timezone

from common import serializers
from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        depth = 1
        exclude = ('name',)

    def create(self, validated_data):
        # Auto generate name
        validated_data['name'] = timezone.now().strftime('%s-%f')
        return Group.objects.create(**validated_data)


class GroupRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')
