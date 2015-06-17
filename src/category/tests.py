from rest_framework import status

from common.tests import TestCase
from . import factories


class TestCategory(TestCase):
    def test_create(self):
        resp = self.admin_client.post('/categories', data=factories.BaseFactory())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_with_parent(self):
        category = factories.CategoryFactory()

        resp = self.admin_client.post('/categories', data=factories.BaseFactory(parent=category.id))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create 3rd level category
        category3 = factories.Sub3CategoryFactory()
        resp = self.admin_client.post('/categories',
                                      data=factories.BaseFactory(parent=category3.id))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data['hierarchy']), 4)
        self.assertEqual(resp.data['parent'], category3.id)
