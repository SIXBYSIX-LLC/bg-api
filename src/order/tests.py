from catalog.models import Product
from common.tests import TestCase
from cart import factories as cart_factories
from charge.factories import SalesTaxFactory
from .constants import Status as sts_const
from .models import Item


class OrderTest(TestCase):
    def prepare_data(self):
        SalesTaxFactory()
        self.cart = cart_factories.CartFactory(
            user=self.dataset.users[1],
            is_active=True,
            location=self.dataset.users[1].address_set.filter(city__name_std='Rajkot')[0],
            billing_address=self.dataset.users[1].address_set.filter(city__name_std='Rajkot')[0]
        )
        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()
        prod2 = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()
        prod3 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()

        cart_factories.RentalItemFactory(cart=self.cart, product=prod1, is_postpaid=True)
        cart_factories.RentalItemFactory(cart=self.cart, product=prod2, is_postpaid=False)
        cart_factories.PurchaseItemFactory(cart=self.cart, product=prod3)

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
        self.assertEqual(len(resp.data['items']), 3)

        c = self.get_client(self.dataset.users[2])
        resp = c.get('/orderlines')
        self.assertEqual(resp.meta['count'], 1)

    def test_add_inventory(self):
        self.prepare_data()

        c = self.get_client(self.dataset.users[1])
        order_resp = c.post('/orders', data={'cart': self.cart.id})

        c = self.get_client(self.dataset.users[2])
        resp = c.get('/orderlines')
        orderline_id = resp.data[0]['id']
        item_id = resp.data[0]['items'][0]['id']
        product_id = resp.data[0]['items'][0]['detail']['id']
        inventories = Product.objects.get(id=product_id).inventory_set

        data = {'inventories': [inventory.id for inventory in inventories.all() if
                                inventory.is_active]}
        resp = c.put('/orderlines/%s/items/%s/inventories' % (orderline_id, item_id), data=data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_204_NO_CONTENT)

        for inv in inventories.all():
            self.assertFalse(inv.is_active)

    def data_test_for_change_status(self):
        self.prepare_data()

        c = self.get_client(self.dataset.users[1])
        order_resp = c.post('/orders', data={'cart': self.cart.id})
        c = self.get_client(self.dataset.users[2])
        resp = c.get('/orderlines')
        orderline_id = resp.data[0]['id']
        item_id = resp.data[0]['items'][0]['id']
        product_id = resp.data[0]['items'][0]['detail']['id']
        inventories = Product.objects.get(id=product_id).inventory_set

        data = {'inventories': [inventories.all()[1].id]}

        for item in Item.objects.filter(orderline_id=orderline_id):
            item.change_status(sts_const.CONFIRMED)

        c.put('/orderlines/%s/items/%s/inventories' % (orderline_id, item_id), data=data)

        return orderline_id, item_id, order_resp.data['id']

    def test_seller_change_approved_status(self):
        orderline_id, item_id, order_id = self.data_test_for_change_status()

        c = self.get_client(self.dataset.users[2])
        resp = c.put('/orderlines/%s/items/%s/actions/change_status' % (orderline_id, item_id),
                     data={'status': sts_const.APPROVED})

        self.assertEqual(resp.status_code, self.status_code.HTTP_204_NO_CONTENT)

    def test_user_change_approved_status(self):
        """
        Ensures user should not be able to change to approved status
        """

        orderline_id, item_id, order_id = self.data_test_for_change_status()

        c = self.get_client(self.dataset.users[1])
        resp = c.put('/orderlines/%s/items/%s/actions/change_status' % (orderline_id, item_id),
                     data={'status': sts_const.APPROVED})

        self.assertEqual(resp.status_code, self.status_code.HTTP_403_FORBIDDEN)

        resp = c.put('/orders/%s/items/%s/actions/change_status' % (order_id, item_id),
                     data={'status': sts_const.APPROVED})
        self.assertEqual(resp.status_code, self.status_code.HTTP_403_FORBIDDEN)

    def test_user_cancel(self):
        orderline_id, item_id, order_id = self.data_test_for_change_status()

        c = self.get_client(self.dataset.users[1])
        resp = c.put('/orders/%s/items/%s/actions/change_status' % (order_id, item_id),
                     data={'status': sts_const.CANCEL})
        self.assertEqual(resp.status_code, self.status_code.HTTP_204_NO_CONTENT)
