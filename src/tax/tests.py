from common.tests import TestCase
import factories


class SalesTaxTest(TestCase):
    def test_create(self):
        st = factories.SalesTaxBaseFactory()
        resp = self.admin_client.post('/taxes/sales_tax', data=st)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)
