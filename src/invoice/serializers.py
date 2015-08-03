from common.serializers import ModelSerializer, rf_serializers
from .models import Invoice, InvoiceLine, Item
from order.serializers import OrderSerializer
from usr.serializers import UserRefSerializer


class ItemSerializer(ModelSerializer):
    user = UserRefSerializer(read_only=True)
    total = rf_serializers.FloatField(read_only=True)

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

        super(ItemSerializer, self).update(instance, validated_data)


class InvoiceSerializer(ModelSerializer):
    order = OrderSerializer(fields=['billing_address', 'shipping_address', 'id'])
    total = rf_serializers.FloatField(read_only=True)
    subtotal = rf_serializers.FloatField(read_only=True)
    shipping_charge = rf_serializers.FloatField(read_only=True)
    additional_charge = rf_serializers.FloatField(read_only=True)
    cost_breakup = rf_serializers.DictField(read_only=True)
    user = UserRefSerializer(read_only=True)

    class Meta:
        model = Invoice


class InvoiceRetrieveSerializer(InvoiceSerializer):
    items = ItemSerializer(many=True, source='item_set')


class InvoiceLineSerializer(InvoiceSerializer):
    invoice = InvoiceSerializer(read_only=True, fields=['order', 'user', 'is_paid'])

    class Meta:
        model = InvoiceLine
        exclude = ('user',)
