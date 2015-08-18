import factory
from factory import fuzzy

from common.faker import fake
from ..models import AdditionalCharge
from .. import constants


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
