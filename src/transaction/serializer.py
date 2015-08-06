from common.serializers import ModelSerializer
from transaction.models import Transaction


class TransactionRefSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ('return_url', 'response')
