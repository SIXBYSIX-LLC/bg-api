from .models import Profile
from common.serializers import ModelSerializer


class LoginSerializer(ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('password', 'unverified_email_key')
