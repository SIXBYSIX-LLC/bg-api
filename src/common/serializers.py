from rest_framework import serializers as rf_serializers
from rest_framework_gis import serializers as rfg_serializers


class Serializer(rf_serializers.Serializer):
    """
    This serializer adds a feature of dynamically allow selection fields in response.

    Inherit this serializer to all serializers
    """

    def __init__(self, *args, **kwargs):
        super(Serializer, self).__init__(*args, **kwargs)

        # Dynamically allow selection of fields
        try:
            fields = self.context.get('request').GET.get('fields')
        except AttributeError:
            fields = None
        if fields:
            fields = fields.split(',')
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ModelSerializer(rf_serializers.ModelSerializer, Serializer):
    @property
    def validated_data(self):
        validated_data = super(Serializer, self).validated_data

        if getattr(self.Meta.model, 'user', None):
            user = self.context['request'].parent_user or self.context['request'].user
            validated_data['user'] = user

        return validated_data


class GeoModelSerializer(rfg_serializers.GeoModelSerializer, ModelSerializer):
    pass
