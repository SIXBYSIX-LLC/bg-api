from datetime import timedelta

import factory
from factory import fuzzy
import dateutil.parser

from catalog.factories import ProductFactory
from common.faker import fake
from ..models import RentalItem, Cart, PurchaseItem
from usr.factories import AddressFactory


class RentalItemBaseFactory(factory.DictFactory):
    date_start = factory.lazy_attribute(
        lambda x: fake.date_time_between(start_date="+5d", end_date="+15d").isoformat()
    )
    date_end = factory.lazy_attribute(
        lambda o: fake.date_time_between(
            start_date=dateutil.parser.parse(o.date_start) + timedelta(days=3),
            end_date="+60d").isoformat()
    )
    shipping_kind = factory.lazy_attribute(
        lambda x: fuzzy.FuzzyChoice(RentalItem.SHIPPING_KIND).fuzz()[0]
    )


class ItemFactory(factory.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    shipping_kind = factory.lazy_attribute(
        lambda x: fuzzy.FuzzyChoice(RentalItem.SHIPPING_KIND).fuzz()[0]
    )


class RentalItemFactory(ItemFactory, factory.DictFactory):
    class Meta:
        model = RentalItem

    date_start = factory.lazy_attribute(
        lambda x: fake.date_time_between(start_date="+3d", end_date="+10d")
    )
    date_end = factory.lazy_attribute(
        lambda o: fake.date_time_between(
            start_date=o.date_start + timedelta(days=3), end_date="+60d"
        )
    )
    shipping_kind = 'delivery'


class PurchaseItemFactory(ItemFactory):
    class Meta:
        model = PurchaseItem


class CartFactory(factory.DjangoModelFactory):
    class Meta:
        model = Cart

    location = factory.SubFactory(AddressFactory)
