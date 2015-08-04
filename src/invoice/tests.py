from common.tests import TestCase
from .models import Invoice


class InvoiceTestCase(TestCase):
    def test_invoice_list(self):
        invoice = self.test_create_invoice()
        c = self.get_client(invoice.user)
        resp = c.get('/invoices')
        self.assertEqual(resp.meta.get('count'), 1, resp)

        resp = c.get('/invoices/%s' % resp.data[0].get('id'))
        self.assertEqual(len(resp.data.get('items')), 1, resp)

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

        self.assertEqual(resp.meta.get('count'), 1, resp)

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
        invoice = Invoice.objects.create_from_order(self.dataset.orders[0])

        return invoice
