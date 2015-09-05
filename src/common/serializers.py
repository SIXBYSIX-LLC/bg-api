"""
===========
Serializers
===========
"""

from rest_framework import serializers as rf_serializers
from rest_framework_gis import serializers as rfg_serializers


class Serializer(rf_serializers.Serializer):
    """
    Base serializer that adds a feature of dynamically allow selection fields in response.
    """

    def __init__(self, *args, **kwargs):
        _fields = kwargs.pop('fields', None)
        super(Serializer, self).__init__(*args, **kwargs)

        # Dynamically allow selection of fields
        try:
            fields = self.context.get('request').GET.get('fields')
        except AttributeError:
            fields = _fields
        if fields:
            if isinstance(fields, basestring):
                fields = fields.split(',')
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ModelSerializer(rf_serializers.ModelSerializer, Serializer):
    """
    Base serializer for model
    """

    @property
    def validated_data(self):
        """
        Overridden method to inject logged in user object to validated_data dict
        """
        validated_data = super(Serializer, self).validated_data

        if getattr(self.Meta.model, 'user', None):
            user = self.context['request'].parent_user or self.context['request'].user
            validated_data['user'] = user

        return validated_data


class GeoModelSerializer(rfg_serializers.GeoModelSerializer, ModelSerializer):
    """
    Base serializer for Geo model
    """
    pass
