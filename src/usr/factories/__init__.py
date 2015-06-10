import factory
from faker import Factory
from factory import fuzzy

from usr.models import Profile
from common.auth.authtoken import Token


fake = Factory.create(locale='en_US')


class TokenFactory(factory.DjangoModelFactory):
    class Meta:
        model = Token

    key = fuzzy.FuzzyText(length=40)


class RegistrationFactory(factory.Factory):
    class Meta:
        model = dict

    email = factory.Sequence(lambda x: fake.email())
    password = '123'
    fullname = factory.LazyAttribute(lambda x: fake.name())
    zip_code = factory.LazyAttribute(lambda x: fake.postcode())
    phone = factory.LazyAttribute(lambda x: fake.phone_number())


class UserFactory(RegistrationFactory, factory.DjangoModelFactory):
    class Meta:
        model = Profile

    is_superuser = False
    is_staff = False
    is_active = True
    auth_token = factory.RelatedFactory(TokenFactory, 'user')
    store_name = factory.LazyAttribute(lambda x: fake.company())


class AdminUserFactory(UserFactory):
    email = factory.Sequence(lambda n: 'admin{0}@example.com'.format(n))
    is_superuser = True
    is_staff = True
