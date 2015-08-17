import random

import factory

from common.faker import fake
from shipping.models import StandardMethod
from usr.factories import AddressFactory


class StandardMethodBaseFactory(factory.DictFactory):
    country = factory.lazy_attribute(lambda x: fake.cities_country().id)
    cost = factory.lazy_attribute(lambda x: fake.pyfloat(left_digits=2, right_digits=2,
                                                         positive=True))
    zipcode_start = factory.lazy_attribute(lambda o: random.randint(360001, 360021))
    zipcode_end = factory.lazy_attribute(lambda o: random.randint(o.zipcode_start, 360021))
    delivery_days = 7
    origin = factory.lazy_attribute(lambda o: AddressFactory(user_id=o.user).id)


class StandardMethodFactory(factory.DjangoModelFactory, StandardMethodBaseFactory):
    class Meta:
        model = StandardMethod

    country = factory.lazy_attribute(lambda x: fake.cities_country())
    origin = factory.lazy_attribute(lambda o: AddressFactory(user=o.user))
