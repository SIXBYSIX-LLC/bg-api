from common.tests import TestCase
import factories
from category.models import Category
from category.factories import Sub3CategoryFactory
from . import constants
from .models import AdditionalCharge


class SalesTaxTest(TestCase):
    def test_create(self):
        st = factories.SalesTaxBaseFactory()
        resp = self.admin_client.post('/charges/sales_taxes', data=st)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)


class AdditionalChargeTest(TestCase):
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

    def test_all_by_natural_key(self):
        categories = Sub3CategoryFactory.create_batch(4)
        # categories = Category.objects.order_by('id').all()[:3]

        # Apply to all
        env = factories.AdditionalChargeFactory(name='Environment fee',
                                                item_kind=constants.ItemKind.ALL,
                                                user=self.user)
        # Apply to only rental item but all categories
        vat = factories.AdditionalChargeFactory(name='VAT', item_kind=constants.ItemKind.RENTAL,
                                                user=self.user)
        # Applies to rental item and category
        cleaning = factories.AdditionalChargeFactory(name='Cleaning',
                                                     item_kind=constants.ItemKind.RENTAL,
                                                     categories=[categories[0]], user=self.user)
        # Applies to all item and only the category
        polish = factories.AdditionalChargeFactory(name='Polishing',
                                                   item_kind=constants.ItemKind.ALL,
                                                   categories=[categories[2]], user=self.user)


        # Ensure rental item only
        a_charges = AdditionalCharge.objects.all_by_natural_key(
            self.user, constants.ItemKind.RENTAL, categories[1])
        self.assertEqual(len(a_charges), 2)
        self.assertIn(env, a_charges)
        self.assertIn(vat, a_charges)

        a_charges = AdditionalCharge.objects.all_by_natural_key(
            self.user, constants.ItemKind.PURCHASE, categories[3])
        self.assertEqual(len(a_charges), 1)
        self.assertIn(env, a_charges)

        # Ensure existed category but item is purchase
        a_charges = AdditionalCharge.objects.all_by_natural_key(
            self.user, constants.ItemKind.PURCHASE, categories[0])
        self.assertEqual(len(a_charges), 1)

        a_charges = AdditionalCharge.objects.all_by_natural_key(
            self.user, constants.ItemKind.RENTAL, categories[0])
        self.assertEqual(len(a_charges), 3, a_charges)
        self.assertIn(env, a_charges)
        self.assertIn(vat, a_charges)
        self.assertIn(cleaning, a_charges)

        a_charges = AdditionalCharge.objects.all_by_natural_key(
            self.user, constants.ItemKind.PURCHASE, categories[2])
        self.assertEqual(len(a_charges), 2, a_charges)
        self.assertIn(env, a_charges)
        self.assertIn(polish, a_charges)
