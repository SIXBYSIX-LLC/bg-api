import json
import logging

from django.conf import settings
from rest_framework.test import APITestCase, APIClient as _APIClient
from rest_framework import status
from django.core.management import call_command

# from mock import patch

from common.factories.dataset import TestDataSet
from usr import factories as usr_factories


class APIClient(_APIClient):
    def get(self, path, data=None, follow=False, **extra):
        response = super(APIClient, self).get(path, data=data, follow=follow, **extra)
        return self._fix_response(response)

    def post(self, path, data=None, format=None, content_type=None, follow=False, **extra):
        response = super(APIClient, self).post(path, data=data, format=format,
                                               content_type=content_type, follow=follow, **extra)

        return self._fix_response(response)

    def put(self, path, data=None, format=None, content_type=None, follow=False, **extra):
        response = super(APIClient, self).put(path, data=data, format=format,
                                              content_type=content_type, follow=follow, **extra)
        return self._fix_response(response)

    def delete(self, path, data=None, format=None, content_type=None, follow=False, **extra):
        response = super(APIClient, self).delete(path, data=data, format=format,
                                                 content_type=content_type, follow=follow, **extra)
        return self._fix_response(response)

    def patch(self, path, data=None, format=None, content_type=None, follow=False, **extra):
        response = super(APIClient, self).patch(path, data=data, format=format,
                                                content_type=content_type, follow=follow, **extra)
        return self._fix_response(response)

    @classmethod
    def _fix_response(cls, response):
        if getattr(response, 'data', None) and response.data.get('count', False) is not False:
            response.meta = response.data
            response.data = json.loads(response.content).get('data')
        return response


class TestCase(APITestCase):
    fixtures = ['country', 'city', 'region']

    def __init__(self, methodName='runTest'):
        super(TestCase, self).__init__(methodName=methodName)

        # Disable logging
        logging.disable(logging.CRITICAL)

    def setUp(self):
        # Syncing permissions
        call_command('syncperms')
        # Turning on debugging
        settings.DEBUG = True

        # Get device token
        self.device = usr_factories.DeviceUserFactory()
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
        self.user = usr_factories.UserFactory(user=self.device)
        self.user_token = self.user.auth_token.key
        # Initiate API Client for Device
        self.user_client = APIClient()
        self.user_client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token)

        self.status_code = status

        self.dataset = TestDataSet()
        self.dataset.generate()

    def get_client(self, user):
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)
        return c

        # def mock_timezone_now(self, time):
        # self.patcher = patch('django.utils.timezone.now', lambda: time)
        #     self.addCleanup(self.patcher.stop)
        #     self.patcher.start()
