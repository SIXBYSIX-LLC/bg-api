import factory

from common.faker import fake


class RentalItemBaseFactory(factory.DictFactory):
    date_start = factory.lazy_attribute(
        lambda x: fake.date_time_between(start_date="+3d", end_date="+10d").isoformat()
    )
    date_end = factory.lazy_attribute(
        lambda o: fake.date_time_between(start_date='+13', end_date="+60d").isoformat()
    )
