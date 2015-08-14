from django.utils import timezone

from common.tests import TestCase
from .models import Invoice
from order import constants as ordr_const


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

    def test_mark_paid(self):
        cart = self.dataset.add_cart(self.dataset.users[1])

        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()
        prod2 = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()

        self.dataset.add_item_to_cart(cart, prod1, 'rental')
        self.dataset.add_item_to_cart(cart, prod2, 'purchase')
        order = self.dataset.add_order(cart)

        invoice = Invoice.objects.create_from_order(order)
        invoice.mark_paid(True)
        invoice.refresh_from_db()

        self.assertTrue(invoice.is_paid)
        self.assertGreater(invoice.order.item_set.filter(statuses__status='confirmed').count(), 0)

    def test_rental_invoice_ongoing_contract(self):
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

        # Ensure pending approved invoice should not be visible to user
        c = self.get_client(invoice.user)
        resp = c.get('/invoices/%s' % invoice.id)
        self.assertEqual(resp.status_code, self.status_code.HTTP_404_NOT_FOUND, resp)

        self.assertGreater(invoice.subtotal, 10)
        self.assertEqual(invoice.item_set.count(), 2)
        self.assertGreater(invoice.cost_breakup['additional_charge']['environment_fee'], 0)

    def test_rental_invoice_multiple_user_order(self):
        cart1 = self.dataset.add_cart(self.dataset.users[1])
        cart2 = self.dataset.add_cart(self.dataset.users[2])

        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()
        prod2 = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()

        self.dataset.add_item_to_cart(cart1, prod1, 'rental',
                                      date_start=timezone.datetime(2015, 7, 1, 10),
                                      date_end=timezone.datetime(2015, 9, 1))
        self.dataset.add_item_to_cart(cart2, prod2, 'rental',
                                      date_start=timezone.datetime(2015, 7, 13, 16, 30),
                                      date_end=timezone.datetime(2015, 9, 15, 20))
        order1 = self.dataset.add_order(cart1, True, True)
        order2 = self.dataset.add_order(cart2, True, True)

        Invoice.objects.create_from_order(order1)
        Invoice.objects.create_from_order(order2)

        invoices = Invoice.objects.generate_rental_invoices(num_days=28)
        self.assertEqual(len(invoices), 2)
        self.assertNotEqual(invoices[0].user, invoices[1].user)

    def test_rental_invoice_end_contract(self):
        cart = self.dataset.add_cart(self.dataset.users[1])

        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()

        self.dataset.add_item_to_cart(cart, prod1, 'rental',
                                      date_start=timezone.datetime(2015, 7, 1, 10),
                                      date_end=timezone.datetime(2015, 8, 11, 12))
        order = self.dataset.add_order(cart, True, True)

        Invoice.objects.create_from_order(order)

        # Shifting now to 11/7 and ending contract
        self.mock_timezone_now(timezone.datetime(2015, 7, 11, 12))
        self.dataset.change_order_status(order, ((ordr_const.Status.END_CONTRACT, None), ))

        # Now shifting now to 13/7 and generating the invoice
        self.mock_timezone_now(timezone.datetime(2015, 7, 13, 12))
        invoices = Invoice.objects.generate_rental_invoices(num_days=28)
        # Ensure that we get the invoice although 28 days are not completed but contract is ended
        self.assertEqual(len(invoices), 1)
        # Ensure date_to should of contract end date
        self.assertEqual(invoices[0].item_set.first().date_to,
                         timezone.datetime(2015, 7, 11, 12, tzinfo=timezone.pytz.UTC))

        # Now shifting time to 15/7 and generate the invoice
        self.mock_timezone_now(timezone.datetime(2015, 7, 15, 12))
        invoices = Invoice.objects.generate_rental_invoices(num_days=28)
        # Ensure we don't get any invoice as the item is already ended
        self.assertEqual(len(invoices), 0)

    def test_rental_invoice_48_days(self):
        cart1 = self.dataset.add_cart(self.dataset.users[1])

        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()

        self.dataset.add_item_to_cart(cart1, prod1, 'rental',
                                      date_start=timezone.datetime(2015, 7, 1, 10),
                                      date_end=timezone.datetime(2016, 9, 1))

        order1 = self.dataset.add_order(cart1, True, True)

        Invoice.objects.create_from_order(order1)

        # Generate 1st invoice for 28 days
        invoices = Invoice.objects.generate_rental_invoices(num_days=28)
        invoice_prev = invoices[0]
        # Ensure that shipping charge is calculated
        self.assertGreater(invoice_prev.item_set.first().shipping_charge, 0)

        # Now mock the time to +30 days to open window for 2nd invoice
        self.mock_timezone_now(invoice_prev.item_set.first().date_to + timezone.timedelta(days=30))

        # Generate 2nd invoice
        invoices = Invoice.objects.generate_rental_invoices(num_days=28)
        invoice_current = invoices[0]
        # Ensure that shipping charge is 0 because system has calculated it before
        self.assertEqual(invoice_current.item_set.first().shipping_charge, 0)

    def test_rental_invoice_approve(self):
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
        invoice = invoices[0]

        self.assertEqual(invoice.invoiceline_set.count(), 2)

        invoicelines = list(invoice.invoiceline_set.all())

        c = self.get_client(invoicelines[0].user)
        resp = c.put('/invoicelines/%s/actions/approve' % invoicelines[0].id)
        self.assertEqual(resp.status_code, self.status_code.HTTP_204_NO_CONTENT)
        # Reload object and ensure it's approved
        invoicelines[0].refresh_from_db()
        self.assertTrue(invoicelines[0].is_approve)

        c = self.get_client(invoicelines[1].user)
        resp = c.put('/invoicelines/%s/actions/approve' % invoicelines[1].id)
        self.assertEqual(resp.status_code, self.status_code.HTTP_204_NO_CONTENT)
        # Reload object and ensure it's approved
        invoicelines[1].refresh_from_db()
        self.assertTrue(invoicelines[1].is_approve)

        c = self.get_client(self.dataset.users[1])
        resp = c.get('/invoices/%s' % invoice.id)
        invoice.refresh_from_db()
        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK)

    def test_rental_invoice_end_running_contract(self):
        cart1 = self.dataset.add_cart(self.dataset.users[1])
        cart2 = self.dataset.add_cart(self.dataset.users[2])

        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()
        prod2 = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()
        prod3 = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()

        self.dataset.add_item_to_cart(cart1, prod1, 'rental',
                                      date_start=timezone.datetime(2015, 7, 1, 10),
                                      date_end=timezone.datetime(2016, 9, 1))
        self.dataset.add_item_to_cart(cart2, prod2, 'rental',
                                      date_start=timezone.datetime(2015, 7, 2, 16, 30),
                                      date_end=timezone.datetime(2015, 9, 15, 20))
        # This item should not be invoiced as it's far away from 28 days
        self.dataset.add_item_to_cart(cart2, prod3, 'rental',
                                      date_start=timezone.datetime(2015, 10, 25, 16, 30),
                                      date_end=timezone.datetime(2015, 9, 15, 20))

        order1 = self.dataset.add_order(cart1, True, True)
        order2 = self.dataset.add_order(cart2, True, True)

        Invoice.objects.create_from_order(order1)
        Invoice.objects.create_from_order(order2)

        # After 15 days, end order 1 item
        self.mock_timezone_now(timezone.datetime(2015, 7, 16, 10))
        self.dataset.change_order_status(order1, ((ordr_const.Status.END_CONTRACT, None), ))

        # Shift now to 21st day of order1 item 1 start date
        self.mock_timezone_now(timezone.datetime(2015, 7, 22, 18))
        invoices = Invoice.objects.generate_rental_invoices(num_days=28)
        # Ensure that we get only 1 invoice as order2's items are far way from 28 days
        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices[0].order, order1)

        # Shift now() to 29th day or order2
        self.mock_timezone_now(timezone.datetime(2015, 7, 31, 23, 59))
        invoices = Invoice.objects.generate_rental_invoices(num_days=28)
        # Ensure that we get only 1 invoice as order1's items are ended and order2's 2nd item is
        # not started yet
        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices[0].order, order2)
        self.assertEqual(invoices[0].item_set.count(), 1)
