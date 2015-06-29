import factory
from cities.models import Region

from common.faker import fake


class SalesTaxBaseFactory(factory.DictFactory):
    country = factory.lazy_attribute(lambda o: fake.cities_country().id)
    state = factory.lazy_attribute(lambda o: fake.cities_region(country=o.country).id)
    name = factory.lazy_attribute(lambda o: 'US %s tax' % Region.objects.get(id=o.state).name)
    unit = 'pct'
    value = factory.lazy_attribute(lambda x: fake.pyfloat(left_digits=1, right_digits=2,
                                                          positive=True))
