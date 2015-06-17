__all__ = ['BaseFactory', 'CategoryFactory', 'Sub1CategoryFactory', 'Sub2CategoryFactory',
           'Sub3CategoryFactory', 'Sub4CategoryFactory']

import factory
from faker import Factory

from ..models import Category


fake = Factory.create(locale='en_US')


class BaseFactory(factory.DictFactory):
    name = factory.lazy_attribute(lambda x: fake.first_name())


class CategoryFactory(factory.DjangoModelFactory, BaseFactory):
    class Meta:
        model = Category


class Sub1CategoryFactory(CategoryFactory):
    parent = factory.SubFactory(CategoryFactory)


class Sub2CategoryFactory(Sub1CategoryFactory):
    parent = factory.SubFactory(Sub1CategoryFactory)


class Sub3CategoryFactory(Sub2CategoryFactory):
    parent = factory.SubFactory(Sub2CategoryFactory)


class Sub4CategoryFactory(Sub3CategoryFactory):
    parent = factory.SubFactory(Sub3CategoryFactory)

