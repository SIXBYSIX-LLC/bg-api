from common.serializers import ModelSerializer, rf_serializers, Serializer
from .models import Invoice, InvoiceLine, Item
from order.serializers import OrderSerializer
from usr.serializers import UserRefSerializer
from common import helper
from transaction import constants as trans_const


class ItemSerializer(ModelSerializer):
    total = rf_serializers.FloatField(read_only=True)
    additional_charge = rf_serializers.FloatField(read_only=True)

    class Meta:
        model = Item
        exclude = ('invoice', 'invoiceline', 'order_item')
        read_only_fields = ('qty', 'date_from', 'date_to')

    def update(self, instance, validated_data):
        # Update only additional charge dict
        cost_breakup = validated_data.get('cost_breakup')
        if cost_breakup:
            additional_charge = cost_breakup.get('additional_charge')
            instance.cost_breakup['additional_charge'] = additional_charge
        instance.full_clean()
        return super(ItemSerializer, self).update(instance, validated_data)


class InvoiceSerializer(ModelSerializer):
    order = OrderSerializer(fields=['billing_address', 'shipping_address', 'id'])
    total = rf_serializers.FloatField(read_only=True)
    subtotal = rf_serializers.FloatField(read_only=True)
    shipping_charge = rf_serializers.FloatField(read_only=True)
    additional_charge = rf_serializers.FloatField(read_only=True)
    cost_breakup = rf_serializers.DictField(read_only=True)
    user = UserRefSerializer(read_only=True, source='user.profile')

    class Meta:
        model = Invoice


class InvoiceRetrieveSerializer(InvoiceSerializer):
    items = ItemSerializer(many=True, source='item_set')


class InvoiceLineSerializer(InvoiceSerializer):
    invoice = InvoiceSerializer(read_only=True, fields=['order', 'user', 'is_paid'])

    class Meta:
        model = InvoiceLine
        exclude = ('user', 'order')
        ready_only_fields = ('is_approve',)


class InvoicePaymentSerializer(Serializer):
    return_url = rf_serializers.URLField()
    gateway = rf_serializers.ChoiceField(helper.prop2pair(trans_const.PaymentGateway))
    nonce = rf_serializers.DictField(required=False)
