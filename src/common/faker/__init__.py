__all__ = ['fake']

from faker.providers import BaseProvider
from cities.models import Country, City, Region
from faker import Factory

fake = Factory.create(locale='en_US')


class CitiesProvider(BaseProvider):
    def cities_country(self, code3=None):
        if code3:
            return Country.objects.get(code3=code3)
        return Country.objects.order_by('?').first()

    def cities_region(self, country):
        return Region.objects.filter(country=country).order_by('?').first()

    def cities_city(self, region):
        return City.objects.filter(region=region).order_by('?').first()


fake.add_provider(CitiesProvider)
