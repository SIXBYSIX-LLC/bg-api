from common.tests import TestCase

from cart import factories as cart_factories
from tax.factories import SalesTaxFactory


class OrderTest(TestCase):
    def prepare_data(self):
        SalesTaxFactory()
        self.cart = cart_factories.CartFactory(
            user=self.dataset.users[1],
            is_active=True,
            location=self.dataset.users[1].address_set.filter(city__name_std='Rajkot')[0]
        )
        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()
        prod2 = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()

        cart_factories.RentalItemFactory(cart=self.cart, product=prod1)
        cart_factories.RentalItemFactory(cart=self.cart, product=prod2)

        self.cart.calculate_cost(force_item_calculation=True)

    def test_create_order(self):
        self.prepare_data()

        c = self.get_client(self.dataset.users[1])
        resp = c.post('/orders', data={'cart': self.cart.id})
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED, resp)

        # Ensure that user's current cart is empty
        resp = c.get('/carts/current')
        self.assertEqual(len(resp.data['rental_products']), 0)

    def test_list_order_user_acl(self):
        self.prepare_data()

        c = self.get_client(self.dataset.users[1])
        order_resp = c.post('/orders', data={'cart': self.cart.id})

        resp = c.get('/orders/%s' % order_resp.data['id'])
        self.assertEqual(len(resp.data['rental_items']), 2)

        c = self.get_client(self.dataset.users[2])
        print self.dataset.users[2].id
        resp = c.get('/orderlines')
        print resp
