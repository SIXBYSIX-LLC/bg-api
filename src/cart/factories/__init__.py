import factory
from factory import fuzzy

from common.faker import fake
from ..models import RentalItem


class RentalItemBaseFactory(factory.DictFactory):
    date_start = factory.lazy_attribute(
        lambda x: fake.date_time_between(start_date="+3d", end_date="+10d").isoformat()
    )
    date_end = factory.lazy_attribute(
        lambda o: fake.date_time_between(start_date='+13', end_date="+60d").isoformat()
    )
    shipping_kind = factory.lazy_attribute(
        lambda x: fuzzy.FuzzyChoice(RentalItem.SHIPPING_KIND).fuzz()[0]
    )
