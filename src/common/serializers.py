from rest_framework import serializers as rf_serializers


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
    pass
