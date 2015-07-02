from cities.models import City
from factory import fuzzy

from usr import factories as usr_factories
from catalog import factories as cat_factories
from shipping import factories as shp_factories


class TestDataSet(object):
    ZIP_RANGE_RAJKOT = 360001, 365480
    ZIP_RANGE_AHMEDABAD = 380001, 383345
    ZIP_RANGE_VADODARA = 388710, 393130
    ZIP_RANGE_SURAT = 392150, 396510

    products = []
    users = []

    def generate(self):
        self.users = usr_factories.UserFactory.create_batch(4)

        for user in self.users:
            ahm = self.add_address(user, 'Ahmedabad')[0]
            vad = self.add_address(user, 'Vadodara')[0]
            srt = self.add_address(user, 'Surat')[0]
            rjt = self.add_address(user, 'Rajkot')[0]

            self.products += self.add_product(user, ahm, 5)
            self.products += self.add_product(user, vad, 5)
            self.products += self.add_product(user, srt, 5)
            self.products += self.add_product(user, rjt, 5)

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

            # Vadodara to Surat
            shp_factories.StandardMethodFactory(origin=vad,
                                                zipcode_start=388710,
                                                zipcode_end=396510,
                                                cost=fuzzy.FuzzyDecimal(6000, 10000).fuzz(),
                                                user=user)

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
