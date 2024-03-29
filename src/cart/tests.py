from django.utils import timezone

from cart.factories import RentalItemBaseFactory, RentalItemFactory, CartFactory
from common.tests import TestCase
from catalog.factories import ProductFactory
from taxrates.models import TaxRate


class CartTestCase(TestCase):
    def get_cart(self):
        # Getting cart id
        resp = self.user_client.get('/carts/current')
        return resp.data['id']

    def test_get_current(self):
        resp = self.user_client.get('/carts/current')
        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK)

    def test_add_rental_product(self):
        cart_id = self.get_cart()

        product = ProductFactory()
        new_rental = RentalItemBaseFactory(product=product.id)
        resp = self.user_client.post('/carts/%s/rentals' % cart_id, data=new_rental)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)

    def test_add_invalid_rental_product(self):
        cart_id = self.get_cart()
        product = ProductFactory(monthly_price=0)

        new_rental = RentalItemBaseFactory(product=product.id)
        resp = self.user_client.post('/carts/%s/rentals' % cart_id, data=new_rental)
        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST)

    def test_update_product(self):
        # Prepare cart
        cart = CartFactory(user=self.dataset.users[1],
                           location=self.dataset.users[1].usr_address_set.first())
        rental_item = RentalItemFactory(cart=cart,
                                        product=self.dataset.users[3].product_set.first())
        c = self.get_client(self.dataset.users[1])

        # Check if update is working
        resp = c.patch('/carts/%s/rentals/%s' % (cart.id, rental_item.id),
                       data={'qty': 3})
        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK)

        # # Ensure product shouldn't be updated
        # new_product = self.dataset.users[3].product_set.first()
        # resp = c.patch('/carts/%s/rentals/%s' % (cart.id, rental_item.id),
        # data={'product': new_product.id})
        # self.assertNotEqual(resp.data['product'], new_product.id)

    def test_minimum_contract_period(self):
        def change_min_contract_period(user, days):
            user.profile.settings.update({'minimum_contract_period': days})
            user.profile.save()

        cart_id = self.get_cart()
        product = ProductFactory()
        change_min_contract_period(product.user, 5)
        new_rental = RentalItemBaseFactory(product=product.id,
                                           date_start='2016-06-01T12:00:00',
                                           date_end='2016-06-02T12:00:00')
        resp = self.user_client.post('/carts/%s/rentals' % cart_id, data=new_rental)
        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST)

        # Prepare cart
        cart = CartFactory(user=self.dataset.users[1],
                           location=self.dataset.users[1].usr_address_set.first())
        rental_item = RentalItemFactory(cart=cart,
                                        product=self.dataset.users[3].product_set.first())
        c = self.get_client(self.dataset.users[1])
        change_min_contract_period(self.dataset.users[3], 5)

        # Check if update is working
        resp = c.patch('/carts/%s/rentals/%s' % (cart.id, rental_item.id),
                       data={'date_start': '2016-06-01T12:00:00',
                             'date_end': '2016-06-02T12:00:00'})
        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST)

    def test_minimum_notice_period(self):
        def change_min_notice_period(user, days):
            user.profile.settings.update({'minimum_rent_notice_period': days})
            user.profile.save()

        cart_id = self.get_cart()
        product = ProductFactory()
        change_min_notice_period(product.user, 3)
        new_rental = RentalItemBaseFactory(product=product.id,
                                           date_start=(timezone.now() + timezone.timedelta(
                                               days=1)).isoformat(),
                                           date_end='2016-06-02T12:00:00')
        resp = self.user_client.post('/carts/%s/rentals' % cart_id, data=new_rental)
        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST)

    def test_is_shippable(self):
        # Cart with shipping address to rajkot
        rjt = self.dataset.users[1].usr_address_set.filter(city__name_std='Rajkot').first()
        cart = CartFactory(user=self.dataset.users[1], location=rjt)

        # Product from Rajkot
        prod = self.dataset.users[3].product_set.filter(
            location__city__name_std='Rajkot').first()
        rental_item = RentalItemBaseFactory(product=prod.id, shipping_kind='delivery')
        c = self.get_client(self.dataset.users[1])
        resp = c.post('/carts/%s/rentals' % cart.id, data=rental_item)
        self.assertTrue(resp.data['rental_products'][0].get('is_shippable'), resp)

        # Product from Ahmedabad
        prod = self.dataset.users[3].product_set.filter(
            location__city__name_std='Ahmedabad').first()
        rental_item = RentalItemBaseFactory(product=prod.id, shipping_kind='delivery')
        resp = c.post('/carts/%s/rentals' % cart.id, data=rental_item)
        self.assertFalse(resp.data.get('is_shippable'))

    def test_no_shipping_cost_when_pickup(self):
        rjt = self.dataset.users[1].usr_address_set.filter(city__name_std='Rajkot').first()
        cart = CartFactory(user=self.dataset.users[1], location=rjt)

        # Product from Rajkot
        prod = self.dataset.users[3].product_set.filter(
            location__city__name_std='Rajkot').first()
        rental_item = RentalItemBaseFactory(product=prod.id, shipping_kind='pickup')
        c = self.get_client(self.dataset.users[1])
        resp = c.post('/carts/%s/rentals' % cart.id, data=rental_item)
        self.assertEqual(resp.data['rental_products'][0].get('shipping_charge'), 0.0, resp)

    def test_cost_update_on_location_change(self):
        srt = self.dataset.users[1].usr_address_set.filter(city__name_std='Surat').first()
        rjt = self.dataset.users[1].usr_address_set.filter(city__name_std='Rajkot').first()
        # Initial cart location is Surat
        cart = CartFactory(user=self.dataset.users[1], location=srt)

        # Product from Rajkot
        prod = self.dataset.users[3].product_set.filter(
            location__city__name_std='Vadodara').first()
        rental_item = RentalItemBaseFactory(product=prod.id, shipping_kind='delivery')
        c = self.get_client(self.dataset.users[1])
        resp = c.post('/carts/%s/rentals' % cart.id, data=rental_item)

        # Now change it to Rajkot
        upresp = c.patch('/carts/%s' % cart.id, data={'location': rjt.id})
        self.assertEqual(upresp.status_code, self.status_code.HTTP_200_OK)
        self.assertNotEqual(upresp.data['rental_products'][0]['shipping_charge'],
                            resp.data['rental_products'][0]['shipping_charge'])

        # Delete item entirely
        c.delete('/carts/%s/rentals/%s' % (cart.id, resp.data['rental_products'][0]['id']))
        rmresp = c.get('/carts/current')
        self.assertEqual(rmresp.data['total'], 0, rmresp)

    def test_cart_sales_tax(self):
        # Cart with shipping address to rajkot
        rjt = self.dataset.users[1].usr_address_set.filter(city__name_std='Rajkot').first()
        cart = CartFactory(user=self.dataset.users[1], location=rjt)

        tax = TaxRate.objects.create(country='IN', state='GJ', zip_code=rjt.zip_code, rate=7.45,
                                     tax_region_name='Rajkot')

        # Product from Rajkot
        prod = self.dataset.users[3].product_set.filter(
            location__city__name_std='Rajkot').first()
        purchase_item = {'product': prod.id, 'shipping_kind': 'delivery'}
        c = self.get_client(self.dataset.users[1])
        c.post('/carts/%s/purchases' % cart.id, data=purchase_item)
        resp = c.get('/carts/current')
        self.assertEqual(resp.data['cost_breakup']['sales_tax_pct'], tax.rate)
        self.assertGreater(resp.data['cost_breakup']['additional_charge']['sales_tax'], 10)

    def test_add_purchases_product(self):
        cart_id = self.get_cart()

        product = ProductFactory()
        new_rental = RentalItemBaseFactory(product=product.id)
        resp = self.user_client.post('/carts/%s/purchases' % cart_id, data=new_rental)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED, resp)
        self.assertEqual(len(resp.data['purchase_products']), 1, resp)

        resp = self.user_client.post('/carts/%s/purchases' % cart_id, data=new_rental)
        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST, resp)

    def test_checkout(self):
        cart = self.dataset.add_cart(self.dataset.users[1])
        cart.billing_address = None
        cart.save(update_fields=['billing_address'])
        cart_id = cart.id
        cart_uri = '/carts/%s/actions/checkout' % cart_id
        prod1 = self.dataset.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()
        c = self.get_client(self.dataset.users[1])

        # We don't have any item in cart and expecting the error
        resp = c.put('/carts/%s/actions/checkout' % cart_id)
        self.assertEqual(resp.status_code, 422)

        # Adding item to cart
        new_rental = RentalItemBaseFactory(product=prod1.id)
        c.post('/carts/%s/purchases' % cart_id, data=new_rental)

        # We don't have billing and shipping address set so expecting the error
        resp = c.put('/carts/%s/actions/checkout' % cart_id)
        self.assertEqual(resp.status_code, 422)

        # Setting the addresses
        address = self.dataset.users[1].usr_address_set.filter(city__name_std='Rajkot').first()
        c.patch('/carts/%s' % cart_id, data={'location': address.id,
                                                            'billing_address': address.id})

        # Now we all good
        resp = c.put(cart_uri)
        self.assertEqual(resp.status_code, self.status_code.HTTP_200_OK, resp)

    def test_contact_info_save(self):
        """ Test if contact information is being saved with validation """

        cart_id = self.get_cart()
        data = {'contact_info': {'name': 'abc', 'phone': '+918080190902'}}
        resp = self.user_client.patch('/carts/%s' % cart_id, data=data, format='json')

        self.assertDictEqual(resp.data.get('contact_info'), data.get('contact_info'))
