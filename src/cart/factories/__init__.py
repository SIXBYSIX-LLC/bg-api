from datetime import timedelta

from django.utils import timezone
import factory
from factory import fuzzy

from catalog.factories import ProductFactory
from ..models import RentalItem, Cart, PurchaseItem
from usr.factories import AddressFactory


class RentalItemBaseFactory(factory.DictFactory):
    date_start = (timezone.now() + timedelta(days=3)).isoformat()
    date_end = (timezone.now() + timedelta(days=30)).isoformat()

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

    date_start = (timezone.now() + timedelta(days=3))
    date_end = (timezone.now() + timedelta(days=30))
    shipping_kind = 'delivery'


class PurchaseItemFactory(ItemFactory):
    class Meta:
        model = PurchaseItem


class CartFactory(factory.DjangoModelFactory):
    class Meta:
        model = Cart

    location = factory.SubFactory(AddressFactory)
