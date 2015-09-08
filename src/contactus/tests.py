from common.tests import TestCase
from . import factories


class ContactUsTest(TestCase):
    def test_create(self):
        data = factories.ContactusBaseFactory()
        resp = self.device_client.post('/contactus', data=data)

        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)
