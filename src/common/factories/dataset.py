from cities.models import City
from factory import fuzzy

from usr import factories as usr_factories
from catalog import factories as cat_factories
from shipping import factories as shp_factories
from cart import factories as cart_factories
from charge import factories as chrg_factories
from order.models import Order
from order import constants as ordr_const
from system.models import Config


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

            self.create_additional_charge(user, 'Environment Fee')

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

        chrg_factories.SalesTaxFactory()
        self.braintree_sandbox_config()

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
        cart = cart_factories.CartFactory(
            user=user,
            is_active=True,
            location=user.usr_address_set.filter(city__name_std='Rajkot')[0],
            billing_address=user.usr_address_set.filter(city__name_std='Rajkot')[0]
        )

        return cart

    def add_item_to_cart(self, cart, product, add_as, **kwargs):
        if add_as == 'purchase':
            cart_factories.PurchaseItemFactory(cart=cart, product=product)
        else:
            cart_factories.RentalItemFactory(cart=cart, product=product, is_postpaid=True, **kwargs)

        cart.calculate_cost(force_item_calculation=True)

    def add_order(self, cart, add_inventory=False, is_delivered=False):
        order = Order.objects.create_order(cart)
        if add_inventory is True:
            for item in order.item_set.all():
                item.add_inventories(*item.product.inventory_set.filter(is_active=True)[:item.qty])

        if add_inventory is True and is_delivered is True:
            self.change_order_status(order, (
                (ordr_const.Status.CONFIRMED, None),
                (ordr_const.Status.APPROVED, None),
                (ordr_const.Status.READY_TO_SHIP, None),
                (ordr_const.Status.DISPATCHED, None),
                (ordr_const.Status.DELIVERED, None))
            )
        return order

    @classmethod
    def change_order_status(cls, order, statuses):
        for item in order.item_set.all():
            for status, info in statuses:
                item.change_status(status, info)

    def create_additional_charge(self, user, name):
        chrg_factories.AdditionalChargeFactory(user=user, item_kind='all', name=name)

    def braintree_sandbox_config(self):
        Config.objects.update_or_create(id='braintree', config={
            'environment': 'Sandbox',
            'merchant_id': 's22q4zwcs8rsdb4y',
            'public_key': '5jbzrdvk5rn9y49z',
            'private_key': '51f2d485949da343465ef953b34cacf5'
        })
