import factory
from factory import fuzzy
from cities.models import Region

from common.faker import fake
from ..models import SalesTax, AdditionalCharge
from .. import constants


class SalesTaxBaseFactory(factory.DictFactory):
    country = factory.lazy_attribute(lambda o: fake.cities_country().id)
    state = factory.lazy_attribute(lambda o: fake.cities_region(country=o.country).id)
    name = factory.lazy_attribute(lambda o: 'US %s tax' % Region.objects.get(id=o.state).name)
    unit = 'pct'
    value = factory.lazy_attribute(lambda x: fake.pyfloat(left_digits=1, right_digits=2,
                                                          positive=True))


class SalesTaxFactory(factory.DjangoModelFactory, factory.DictFactory):
    class Meta:
        model = SalesTax

    country = factory.lazy_attribute(lambda o: fake.cities_country())
    state = factory.lazy_attribute(lambda o: fake.cities_region(country=o.country))
    unit = 'pct'
    value = factory.lazy_attribute(lambda x: fake.pyfloat(left_digits=1, right_digits=2,
                                                          positive=True))


class AdditionalChargeBaseFactory(factory.DictFactory):
    unit = 'pct'
    value = factory.lazy_attribute(lambda x: fake.pyfloat(left_digits=1, right_digits=2,
                                                          positive=True))
    item_kind = fuzzy.FuzzyChoice([constants.ItemKind.PURCHASE, constants.ItemKind.RENTAL,
                                   constants.ItemKind.ALL])


class AdditionalChargeFactory(factory.DjangoModelFactory, AdditionalChargeBaseFactory):
    class Meta:
        model = AdditionalCharge

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for categories in extracted:
                self.categories.add(categories)
