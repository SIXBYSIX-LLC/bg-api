from common.tests import TestCase
from . import factories
from category import factories as cat_factories


class ProductTest(TestCase):
    def test_create(self):
        data = factories.ProductBaseFactory(user_id=self.user.id)

        resp = self.user_client.post('/products', data=data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)

    def test_create_parent_user(self):
        """
        Test product creation with user member
        """
        member = factories.UserFactory(user=self.user)
        data = factories.ProductBaseFactory(user_id=member.id)
        member_client = self.get_client(member)

        resp = member_client.post('/products', data=data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)
        self.assertEqual(resp.data['user'], self.user.id)

    def test_create_with_sku(self):
        SKU = 'abcxyz'
        data = factories.ProductBaseFactory(user_id=self.user.id, sku=SKU)

        resp = self.user_client.post('/products', data=data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)
        self.assertEqual(resp.data['sku'], SKU)

    def test_create_negative_price(self):
        data = factories.ProductBaseFactory(user_id=self.user.id, daily_price=-9999999.56)
        resp = self.user_client.post('/products', data=data)

        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST)

    def test_create_with_tags(self):
        TAGS = ['abc', 'xyz']
        data = factories.ProductBaseFactory(user_id=self.user.id, tags=TAGS)

        resp = self.user_client.post('/products', data=data, format='json')
        self.assertEqual(resp.data['tags'], TAGS)

    def test_create_with_non_leaf_category(self):
        category = cat_factories.Sub4CategoryFactory()

        # Root category
        data = factories.ProductBaseFactory(user_id=self.user.id, category=category.hierarchy[0])
        resp = self.user_client.post('/products', data=data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST)

        # 2nd category
        data = factories.ProductBaseFactory(user_id=self.user.id, category=category.hierarchy[1])
        resp = self.user_client.post('/products', data=data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST)
