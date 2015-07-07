import factory
from factory import fuzzy
from faker import Factory

from category.factories import Sub2CategoryFactory
from ..models import Product, Inventory
from usr.factories import UserFactory, AddressFactory


fake = Factory.create(locale='en_US')


class ProductBaseFactory(factory.DictFactory):
    name = factory.LazyAttribute(lambda x: fake.first_name())
    description = factory.LazyAttribute(lambda x: fake.paragraphs(nb=2))
    brand = factory.lazy_attribute(lambda x: fake.company())
    daily_price = factory.lazy_attribute(lambda x: fake.pyfloat(left_digits=4, right_digits=2,
                                                                positive=True))
    weekly_price = factory.lazy_attribute(lambda x: fake.pyfloat(left_digits=4, right_digits=2,
                                                                 positive=True))
    monthly_price = factory.lazy_attribute(lambda x: fake.pyfloat(left_digits=4, right_digits=2,
                                                                  positive=True))
    sell_price = factory.lazy_attribute(lambda x: fake.pyfloat(left_digits=4, right_digits=2,
                                                               positive=True))
    category = factory.lazy_attribute(lambda x: Sub2CategoryFactory().id)
    tags = ['excavator', 'pornition', 'bob builder']
    condition = 'used'
    location = factory.lazy_attribute(lambda o: AddressFactory(user_id=o.user_id).id)
    sku = ''


class ProductFactory(factory.DjangoModelFactory, ProductBaseFactory):
    class Meta:
        model = Product

    user = factory.SubFactory(UserFactory)
    location = factory.lazy_attribute(lambda o: AddressFactory(user=o.user))
    category = factory.lazy_attribute(lambda x: Sub2CategoryFactory())

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class.objects.create_product(*args, **kwargs)
        return obj


class InventoryBaseFactory(factory.DictFactory):
    serial_no = fuzzy.FuzzyText(length=10)
    source = fuzzy.FuzzyChoice(['purchased', 'rented'])
    is_active = fuzzy.FuzzyChoice([True, False])


class InventoryFactory(factory.DjangoModelFactory, InventoryBaseFactory):
    class Meta:
        model = Inventory
