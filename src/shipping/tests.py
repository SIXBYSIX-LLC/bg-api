from common.tests import TestCase
import factories


class StandardShippingText(TestCase):
    def test_create_standardmethod_rule(self):
        standarmethod = factories.StandardMethodBaseFactory(user=self.user.id)
        resp = self.user_client.post('/settings/shipping/standard', data=standarmethod)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)
