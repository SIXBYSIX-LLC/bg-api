from common.serializers import ModelSerializer

from .models import ContactUs


class ContactUsSerializer(ModelSerializer):
    class Meta:
        model = ContactUs
