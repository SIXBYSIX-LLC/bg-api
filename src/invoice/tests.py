from common.tests import TestCase
from .models import Invoice


class InvoiceTestCase(TestCase):
    def test_invoice_list(self):
        invoice = self.test_create_invoice()
        c = self.get_client(invoice.user)
        resp = c.get('/invoices')
        self.assertEqual(resp.meta.get('count'), 1, resp)

        resp = c.get('/invoices/%s' % resp.data[0].get('id'))
        self.assertEqual(len(resp.data.get('items')), 3, resp)

    def test_invoiceline_list(self):
        self.test_create_invoice()
        c = self.get_client(self.dataset.users[2])
        resp = c.get('/invoicelines')
        self.assertEqual(resp.meta.get('count'), 1, resp)

    def test_invoiceline_item_list(self):
        self.test_create_invoice()
        c = self.get_client(self.dataset.users[2])
        resp = c.get('/invoicelines')
        resp = c.get('/invoicelines/%s/items' % resp.data[0].get('id'))

        self.assertEqual(resp.meta.get('count'), 2, resp)

    def test_invoiceline_edit_item(self):
        self.test_create_invoice()
        c = self.get_client(self.dataset.users[2])
        resp = c.get('/invoicelines')
        invoiceline_id = resp.data[0].get('id')
        resp = c.get('/invoicelines/%s/items' % invoiceline_id)

        # Try to edit approve item
        data = {'subtotal': 530.32}
        resp = c.patch('/invoicelines/%s/items/%s' % (invoiceline_id, resp.data[0].get('id')),
                       data=data)
        self.assertEqual(resp.status_code, 422, resp)

    def test_create_invoice(self):
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

        invoice = Invoice.objects.create_from_order(order)

        return invoice

    def test_create_invoice_only_rental(self):
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
        resp = c.get('/invoices')
        self.assertEqual(resp.meta.get('count'), 1, resp)

        resp = c.get('/invoices/%s' % resp.data[0].get('id'))
        self.assertEqual(len(resp.data.get('items')), 2, resp)
