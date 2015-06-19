import factory
from faker import Factory

from category.factories import Sub2CategoryFactory
from ..models import Product
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
