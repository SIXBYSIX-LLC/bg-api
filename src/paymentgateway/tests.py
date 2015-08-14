from django.utils import timezone

from common.tests import TestCase
from invoice.models import Invoice
from transaction.constants import Status as status_const


class BraintreeTestCase(TestCase):
    # noinspection PyUnresolvedReferences
    from braintree.test.nonces import Nonces

    def prepare_invoice(self):
        cart = self.dataset.add_cart(self.dataset.users[1])

        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()
        prod2 = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()
        prod3 = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()

        self.dataset.add_item_to_cart(cart, prod1, 'rental',
                                      date_start=timezone.datetime(2015, 7, 1, 10),
                                      date_end=timezone.datetime(2015, 9, 1))
        self.dataset.add_item_to_cart(cart, prod2, 'rental',
                                      date_start=timezone.datetime(2015, 7, 13, 16, 30),
                                      date_end=timezone.datetime(2015, 9, 15, 20))
        # This item should not be invoiced as it's far away from 28 days
        self.dataset.add_item_to_cart(cart, prod3, 'rental',
                                      date_start=timezone.datetime(2015, 7, 25, 16, 30),
                                      date_end=timezone.datetime(2015, 9, 15, 20))
        order = self.dataset.add_order(cart, True, True)

        Invoice.objects.create_from_order(order)

        invoices = Invoice.objects.generate_rental_invoices(num_days=28)
        self.assertEqual(len(invoices), 1)
        invoice = invoices[0]

        invoice.approve(force=True)

        return invoice

    def test_invoice_pay_success(self):
        invoice = self.prepare_invoice()

        c = self.get_client(self.dataset.users[1])
        resp = c.post('/invoices/%s/actions/pay' % invoice.id, data={
            'gateway': 'braintree',
            'return_url': 'http://example.com/payment/result',
            'nonce': {
                'payment_method_nonce': self.Nonces.Transactable
            }
        }, format='json')

        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK)
        self.assertEqual(resp.data['transaction']['status'], status_const.SUCCESS, resp)

    def test_invoice_pay_fail(self):
        invoice = self.prepare_invoice()

        c = self.get_client(self.dataset.users[1])
        resp = c.post('/invoices/%s/actions/pay' % invoice.id, data={
            'gateway': 'braintree',
            'return_url': 'http://example.com/payment/result',
            'nonce': {
                'payment_method_nonce': self.Nonces.Consumed
            }
        }, format='json')

        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK)
        self.assertEqual(resp.data['transaction']['status'], status_const.FAIL, resp)

    def test_generate_token(self):
        resp = self.user_client.get('/paymentgateway/braintree/actions/generate_token')

        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK)
        self.assertIsNotNone(resp.data['client_token'])


class PostpaidTestCase(TestCase):
    def test_payment_zero_amount(self):
        cart = self.dataset.add_cart(self.dataset.users[1])

        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()
        prod2 = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()

        self.dataset.add_item_to_cart(cart, prod1, 'rental')
        self.dataset.add_item_to_cart(cart, prod2, 'rental')
        order = self.dataset.add_order(cart)

        invoice = Invoice.objects.create_from_order(order)

        c = self.get_client(invoice.user)
        resp = c.post('/invoices/%s/actions/pay' % invoice.id, data={
            'gateway': 'postpaid', 'return_url': 'http://example.com'
        })
        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK, resp)

    def test_payment_postpaid_non_zero_amount(self):
        cart = self.dataset.add_cart(self.dataset.users[1])

        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()
        prod2 = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()

        self.dataset.add_item_to_cart(cart, prod1, 'rental')
        self.dataset.add_item_to_cart(cart, prod2, 'purchase')
        order = self.dataset.add_order(cart)

        invoice = Invoice.objects.create_from_order(order)

        c = self.get_client(invoice.user)
        resp = c.post('/invoices/%s/actions/pay' % invoice.id, data={
            'gateway': 'postpaid', 'return_url': 'http://example.com'
        })
        self.assertEqual(resp.status_code, 422, resp)
