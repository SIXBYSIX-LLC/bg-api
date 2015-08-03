from cart.factories import RentalItemBaseFactory, RentalItemFactory, CartFactory
from common.tests import TestCase
from catalog.factories import ProductFactory
from charge.factories import SalesTaxFactory


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
                           location=self.dataset.users[1].address_set.first())
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
        cart_id = self.get_cart()

        product = ProductFactory()
        new_rental = RentalItemBaseFactory(product=product.id,
                                           date_start='2016-06-01T12:00:00',
                                           date_end='2016-06-02T12:00:00')
        resp = self.user_client.post('/carts/%s/rentals' % cart_id, data=new_rental)
        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST)

        # Prepare cart
        cart = CartFactory(user=self.dataset.users[1],
                           location=self.dataset.users[1].address_set.first())
        rental_item = RentalItemFactory(cart=cart,
                                        product=self.dataset.users[3].product_set.first())
        c = self.get_client(self.dataset.users[1])

        # Check if update is working
        resp = c.patch('/carts/%s/rentals/%s' % (cart.id, rental_item.id),
                       data={'date_start': '2016-06-01T12:00:00',
                             'date_end': '2016-06-02T12:00:00'})
        self.assertEqual(resp.status_code, self.status_code.HTTP_400_BAD_REQUEST)

    def test_is_shippable(self):
        # Cart with shipping address to rajkot
        rjt = self.dataset.users[1].address_set.filter(city__name_std='Rajkot').first()
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
        rjt = self.dataset.users[1].address_set.filter(city__name_std='Rajkot').first()
        cart = CartFactory(user=self.dataset.users[1], location=rjt)

        # Product from Rajkot
        prod = self.dataset.users[3].product_set.filter(
            location__city__name_std='Rajkot').first()
        rental_item = RentalItemBaseFactory(product=prod.id, shipping_kind='pickup')
        c = self.get_client(self.dataset.users[1])
        resp = c.post('/carts/%s/rentals' % cart.id, data=rental_item)
        self.assertEqual(resp.data['rental_products'][0].get('shipping_charge'), 0.0, resp)

    def test_cost_update_on_location_change(self):
        srt = self.dataset.users[1].address_set.filter(city__name_std='Surat').first()
        rjt = self.dataset.users[1].address_set.filter(city__name_std='Rajkot').first()
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
        tax = SalesTaxFactory()
        # Cart with shipping address to rajkot
        rjt = self.dataset.users[1].address_set.filter(city__name_std='Rajkot').first()
        cart = CartFactory(user=self.dataset.users[1], location=rjt)

        # Product from Rajkot
        prod = self.dataset.users[3].product_set.filter(
            location__city__name_std='Rajkot').first()
        rental_item = RentalItemBaseFactory(product=prod.id, shipping_kind='delivery')
        c = self.get_client(self.dataset.users[1])
        c.post('/carts/%s/rentals' % cart.id, data=rental_item)
        resp = c.get('/carts/current')
        self.assertEqual(resp.data['cost_breakup']['sales_tax_pct'], tax.value)
        self.assertGreater(resp.data['cost_breakup']['sales_tax'], 10)

    def test_add_purchases_product(self):
        cart_id = self.get_cart()

        product = ProductFactory()
        new_rental = RentalItemBaseFactory(product=product.id)
        resp = self.user_client.post('/carts/%s/purchases' % cart_id, data=new_rental)
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED, resp)
