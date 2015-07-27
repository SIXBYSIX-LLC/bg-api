from common.tests import TestCase
import factories
from category.models import Category


class SalesTaxTest(TestCase):
    def test_create(self):
        st = factories.SalesTaxBaseFactory()
        resp = self.admin_client.post('/charges/sales_taxes', data=st)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)


class AdditionalChargeText(TestCase):
    def test_create(self):
        st = factories.AdditionalChargeBaseFactory()
        resp = self.user_client.post('/charges/additional_charges', data=st)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)

    def test_create_with_categories(self):
        categories = Category.objects.values_list('id').order_by('?').all()[:3]
        categories = [v[0] for v in categories]
        st = factories.AdditionalChargeBaseFactory(name='environment', categories=categories)
        resp = self.user_client.post('/charges/additional_charges', data=st)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED, resp)
        self.assertEqual(len(resp.data['categories']), len(categories), resp)
