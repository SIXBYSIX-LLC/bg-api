from common.tests import TestCase

from cart import factories as cart_factories
from tax.factories import SalesTaxFactory


class OrderTest(TestCase):
    def test_create_order(self):
        SalesTaxFactory()
        cart = cart_factories.CartFactory(
            user=self.dataset.users[1],
            is_active=True,
            location=self.dataset.users[1].address_set.filter(city__name_std='Rajkot')[0]
        )
        cart_factories.RentalItemFactory(
            cart=cart,
            product=self.dataset.users[2].product_set.filter(
                location__city__name_std='Surat').order_by('?').first()
        )
        cart.calculate_cost(force_item_calculation=True)

        c = self.get_client(self.dataset.users[1])
        resp = c.post('/orders', data={'cart': cart.id})

        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED, resp)
