from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.management import call_command

from usr import factories as usr_factories


class TestCase(APITestCase):
    fixtures = ['country', 'city', 'region']

    def setUp(self):
        # Turning on debugging
        settings.DEBUG = True

        # Get device token
        self.device = usr_factories.UserFactory()
        self.device_token = self.device.auth_token.key
        # Initiate API Client for Device
        self.device_client = APIClient()
        self.device_client.credentials(HTTP_AUTHORIZATION='Token ' + self.device_token)

        # Get admin token
        self.admin = usr_factories.AdminUserFactory()
        self.admin_token = self.admin.auth_token.key
        # Initiate API Client for Admin
        self.admin_client = APIClient()
        self.admin_client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)

        # User token
        self.user = usr_factories.UserFactory()
        self.user_token = self.device.auth_token.key
        # Initiate API Client for Device
        self.user_client = APIClient()
        self.user_client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)

        call_command('syncperms')
        self.status_code = status

    def get_client(self, user):
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)
        return c

