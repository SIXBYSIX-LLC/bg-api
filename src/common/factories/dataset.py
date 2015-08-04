from cities.models import City
from factory import fuzzy

from usr import factories as usr_factories
from catalog import factories as cat_factories
from shipping import factories as shp_factories
from cart import factories as cart_factories
from charge import factories as chrg_factories
from order.models import Order


class TestDataSet(object):
    ZIP_RANGE_RAJKOT = 360001, 365480
    ZIP_RANGE_AHMEDABAD = 380001, 383345
    ZIP_RANGE_VADODARA = 388710, 393130
    ZIP_RANGE_SURAT = 392150, 396510

    products = []
    users = []
    carts = []
    orders = []

    def generate(self):
        self.users = usr_factories.UserFactory.create_batch(4)

        for user in self.users:
            ahm = self.add_address(user, 'Ahmedabad')[0]
            vad = self.add_address(user, 'Vadodara')[0]
            srt = self.add_address(user, 'Surat')[0]
            rjt = self.add_address(user, 'Rajkot')[0]

            prods_ahm = self.add_product(user, ahm, 5)
            prods_vad = self.add_product(user, vad, 5)
            prods_srt = self.add_product(user, srt, 5)
            prods_rjt = self.add_product(user, rjt, 5)

            self.products += prods_ahm
            self.products += prods_vad
            self.products += prods_srt
            self.products += prods_rjt


            # Rajkot to Rajkot
            shp_factories.StandardMethodFactory(origin=rjt,
                                                zipcode_start=360001,
                                                zipcode_end=365480,
                                                cost=fuzzy.FuzzyDecimal(2000, 5000).fuzz(),
                                                user=user)
            # Ahmedabad to Vadodara
            shp_factories.StandardMethodFactory(origin=ahm,
                                                zipcode_start=380001,
                                                zipcode_end=393130,
                                                cost=fuzzy.FuzzyDecimal(5000, 7000).fuzz(),
                                                user=user)

            # rajkot to Vadodara
            shp_factories.StandardMethodFactory(origin=vad,
                                                zipcode_start=360001,
                                                zipcode_end=365480,
                                                cost=fuzzy.FuzzyDecimal(5000, 7000).fuzz(),
                                                user=user)

            # Vadodara to Surat
            shp_factories.StandardMethodFactory(origin=vad,
                                                zipcode_start=388710,
                                                zipcode_end=396510,
                                                cost=fuzzy.FuzzyDecimal(6000, 10000).fuzz(),
                                                user=user)
        for product in self.products:
            self.add_inventory(product, is_active=True, batch_size=4)
            self.add_inventory(product, is_active=False, batch_size=1)

        self.carts.append(self.add_cart(self.users[1]))
        self.orders.append(self.add_order(self.carts[0]))

    def add_address(self, to_user, city_name, batch_size=1):
        zip_code = getattr(self, 'ZIP_RANGE_%s' % city_name.upper())

        city = City.objects.get(name_std=city_name.capitalize())
        zip_code = fuzzy.FuzzyInteger(*zip_code).fuzz()

        return usr_factories.AddressFactory.create_batch(batch_size, city=city, zip_code=zip_code,
                                                         user=to_user)

    def add_product(self, to_user, location, batch_size=1):
        return cat_factories.ProductFactory.create_batch(
            batch_size,
            user=to_user,
            location=location
        )

    def add_inventory(self, to_proudct, batch_size=1, **kwargs):
        return cat_factories.InventoryFactory.create_batch(batch_size, product=to_proudct,
                                                           user=to_proudct.user, **kwargs)

    def add_cart(self, user):
        chrg_factories.SalesTaxFactory()
        cart = cart_factories.CartFactory(
            user=user,
            is_active=True,
            location=user.address_set.filter(city__name_std='Rajkot')[0],
            billing_address=user.address_set.filter(city__name_std='Rajkot')[0]
        )
        prod1 = self.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()
        prod2 = self.users[3].product_set.filter(
            location__city__name_std='Vadodara').order_by('?').first()
        prod3 = self.users[2].product_set.filter(
            location__city__name_std='Rajkot').order_by('?').first()

        cart_factories.RentalItemFactory(cart=cart, product=prod1, is_postpaid=True)
        cart_factories.RentalItemFactory(cart=cart, product=prod2, is_postpaid=False)
        cart_factories.PurchaseItemFactory(cart=cart, product=prod3)

        cart.calculate_cost(force_item_calculation=True)

        return cart

    def add_order(self, cart):
        return Order.objects.create_order(cart)
