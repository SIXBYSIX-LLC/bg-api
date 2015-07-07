import factory
from factory import fuzzy

from group.models import Group
from usr.models import Profile, Address
from common.auth.authtoken import Token
from common.faker import fake


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

    @factory.post_generation
    def default_group(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        self.groups.add(Group.objects.get(name='User'))

    @factory.post_generation
    def groups(self, create, groups, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if groups:
            # A list of groups were passed in, use them
            for group in groups:
                self.groups.add(group)


class AdminUserFactory(UserFactory):
    email = factory.Sequence(lambda n: 'admin{0}@example.com'.format(n))
    is_superuser = True
    is_staff = True


class DeviceUserFactory(UserFactory):
    email = factory.Sequence(lambda n: 'device{0}@example.com'.format(n))
    is_staff = True

    @factory.post_generation
    def default_group(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        self.groups.add(Group.objects.get(name='Device'))


class AddressBaseFactory(factory.DictFactory):
    name = factory.LazyAttribute(lambda x: fake.name() + fuzzy.FuzzyText().fuzz())
    address1 = factory.LazyAttribute(lambda x: fake.address())
    country = factory.LazyAttribute(lambda x: fake.cities_country().id)
    state = factory.LazyAttribute(lambda o: fake.cities_region(o.country).id)
    city = factory.LazyAttribute(lambda o: fake.cities_city(o.state).id)
    zip_code = fuzzy.FuzzyInteger(360001, 396590)
    kind = Address.Const.TYPE_JOB_SITE


class AddressFactory(factory.DjangoModelFactory, AddressBaseFactory):
    class Meta:
        model = Address

    country = factory.LazyAttribute(lambda x: fake.cities_country())
    state = factory.LazyAttribute(lambda o: fake.cities_region(o.country))
    city = factory.LazyAttribute(lambda o: fake.cities_city(o.state))
