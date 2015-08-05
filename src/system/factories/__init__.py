import factory
from factory import fuzzy

from ..models import Config


class ConfigDataFactory(factory.DictFactory):
    api_key = fuzzy.FuzzyText()
    api_secret = fuzzy.FuzzyText()


class ConfigBaseFactory(factory.DictFactory):
    config = factory.SubFactory(ConfigDataFactory)


class ConfigFactory(factory.DjangoModelFactory, ConfigBaseFactory):
    class Meta:
        model = Config
