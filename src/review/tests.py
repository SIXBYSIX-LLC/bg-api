from common.tests import TestCase
from . import constants


class ReviewTestCase(TestCase):
    def create_order(self):
        cart = self.dataset.add_cart(self.dataset.users[1])

        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()
        prod2 = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()
        prod3 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()

        self.dataset.add_item_to_cart(cart, prod1, 'rental')
        self.dataset.add_item_to_cart(cart, prod2, 'rental')
        self.dataset.add_item_to_cart(cart, prod3, 'purchase')
        order = self.dataset.add_order(cart)

        self.order_items = list(order.item_set.all())

        self.data = {'rating': 3, 'comment': 'nice', 'order_item': self.order_items[1].id}

        return order

    def test_create_review(self):
        self.create_order()

        # Buyer write the review
        c = self.get_client(self.dataset.users[1])
        resp = c.post('/reviews', data=self.data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)
        self.assertEqual(resp.data.get('reviewer'), constants.Reviewer.BUYER)

        # Seller writes the review
        c = self.get_client(self.order_items[1].orderline.user)
        resp = c.post('/reviews', data=self.data)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)
        self.assertEqual(resp.data.get('reviewer'), constants.Reviewer.SELLER)

    def test_create_review_other_user(self):
        """
        Ensure fail when 3rd user tries to write a review
        """
        self.create_order()

        c = self.get_client(self.dataset.users[2])
        resp = c.post('/reviews', data=self.data)
        self.assertEqual(resp.status_code, 422)

