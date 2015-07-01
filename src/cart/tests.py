from cart.factories import RentalItemBaseFactory
from common.tests import TestCase
from catalog.factories import ProductFactory


class CartTestCase(TestCase):
    def get_cart(self):
        # Getting cart id
        resp = self.user_client.get('/cart/current')
        return resp.data['id']

    def test_get_current(self):
        resp = self.user_client.get('/cart/current')
        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK)

    def test_add_rental_product(self):
        cart_id = self.get_cart()

        product = ProductFactory()
        new_rental = RentalItemBaseFactory(product=product.id)
        resp = self.user_client.post('/cart/%s/rental_products' % cart_id, data=new_rental)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)

    def test_add_invalid_rental_product(self):
        cart_id = self.get_cart()
        product = ProductFactory(monthly_price=0)

        new_rental = RentalItemBaseFactory(product=product.id)
        resp = self.user_client.post('/cart/%s/rental_products' % cart_id, data=new_rental)
        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST)

