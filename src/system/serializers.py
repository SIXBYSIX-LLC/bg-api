from common.serializers import ModelSerializer
from system.models import Config


class ConfigSerializer(ModelSerializer):
    class Meta:
        model = Config
        exclude = ('id',)
