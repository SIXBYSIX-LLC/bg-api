from common import serializers
from common.serializers import rf_serializers
from inquiry.models import Thread, Message


class ThreadSerializer(serializers.ModelSerializer):
    text = rf_serializers.CharField(required=False, max_length=1000)
    thread = rf_serializers.SerializerMethodField('get_thread_id', read_only=True)
    unread_count = rf_serializers.IntegerField(read_only=True)

    class Meta:
        model = Thread
        write_only_fields = ('text',)

    def create(self, validated_data):
        return Thread.objects.create_thread(**validated_data)

    def get_thread_id(self, obj):
        return obj.id


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
