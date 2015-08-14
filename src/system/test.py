from common.tests import TestCase
import factories


class ConfigTestCase(TestCase):
    def test_create(self):
        data = factories.ConfigBaseFactory()

        resp = self.admin_client.put('/system/configs/braintree', data=data, format='json')
        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK)

    def test_retrieve(self):
        resp = self.admin_client.get('/system/configs/braintree')
        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK)
