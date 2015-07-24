from common.tests import TestCase
from . import factories
from category import factories as cat_factories
from .models import Product


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

    def test_create_with_inventory(self):
        data = factories.ProductBaseFactory(user_id=self.user.id, qty=30)

        resp = self.user_client.post('/products', data=data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)

    def test_listing_with_qty_field(self):
        factories.ProductFactory.create_batch(2, user=self.user, qty=30)
        resp = self.user_client.get('/products', data={'user': self.user.id})
        self.assertEqual(resp.data[0].get('qty'), 30)

    def test_available_shipping_methods(self):
        product = Product.objects.filter(location__city__name_std='Rajkot').first()
        data = {'country': product.location.country_id, 'zip_code': 360001}
        resp = self.user_client.get('/products/%s/available_shippings' % product.id, data=data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK)
        self.assertEqual(resp.data['standard_shipping']['country'], 1269750)

        data = {'country': product.location.country_id, 'zip_code': 388710}
        resp = self.user_client.get('/products/%s/available_shippings' % product.id, data=data)
        self.assertIsNone(resp.data['standard_shipping'], resp)


class InventoryTest(TestCase):
    def test_add_inventory(self):
        product = factories.ProductFactory(user=self.user)
        inventory = factories.InventoryBaseFactory()

        resp = self.user_client.post('/products/%s/inventories' % product.id, data=inventory)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)

    def test_list_inventory(self):
        products = factories.ProductFactory.create_batch(2, user=self.user)

        for i in xrange(10):
            inventory = factories.InventoryBaseFactory()
            self.user_client.post('/products/%s/inventories' % products[0].id, data=inventory)

        for i in xrange(5):
            inventory = factories.InventoryBaseFactory()
            self.user_client.post('/products/%s/inventories' % products[1].id, data=inventory)

        # check product 1
        resp = self.user_client.get('/products/%s/inventories' % products[0].id)
        self.assertEqual(resp.meta.get('count'), 10)

        resp = self.user_client.get('/products/%s/inventories' % products[1].id)
        self.assertEqual(resp.meta.get('count'), 5)


class InventoryPermissionTest(TestCase):
    def test_create_to_other_user_product(self):
        product = factories.ProductFactory(user=self.user)
        inventory = factories.InventoryBaseFactory()

        user = factories.UserFactory()
        user_client = self.get_client(user)

        resp = user_client.post('/products/%s/inventories' % product.id, data=inventory)
        self.assertEqual(resp.status_code, self.status_code.HTTP_403_FORBIDDEN)

    def test_list_other_user_inventory(self):
        product = factories.ProductFactory(user=self.user)
        factories.InventoryFactory(product=product, user=self.user)

        user = factories.UserFactory()
        user_client = self.get_client(user)

        resp = user_client.get('/products/%s/inventories' % product.id)
        self.assertEqual(resp.meta['count'], 0)
