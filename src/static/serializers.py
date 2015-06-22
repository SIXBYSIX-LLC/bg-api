from common import serializers

from models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('target', 'target_id', 'url', 'id')
        read_only_fields = ('url',)

    def create(self, validated_data):
        return File.objects.upload(self.context['request'].FILES['file'], **validated_data)


class FileRefSerializer(FileSerializer):
    class Meta(FileSerializer.Meta):
        fields = ('url', 'id')
