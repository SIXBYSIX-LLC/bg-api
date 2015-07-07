import csv
from binascii import crc32

from django.core.management.base import BaseCommand
from cities.models import Region, Country

from usr import factories as usr_factories
from usr.models import Profile, Address
from catalog.models import Product
from category.models import Category
from catalog.factories import ProductFactory, InventoryFactory


class Command(BaseCommand):
    args = '<csvfile>'
    help = 'Load specific csv file'

    def handle(self, *args, **options):
        self.seed(args[0])

    def seed(self, f):
        user = self.get_user()
        address = self.get_address(user)
        self.parse_csv(f, address)


    def get_user(self):
        try:
            user = Profile.objects.get(email='user@merchant.com')
        except Profile.DoesNotExist:
            user = usr_factories.UserFactory(email='user@merchant.com')

        return user

    def get_address(self, user):
        try:
            address = Address.objects.get(name='Jobsite 1', user=user)
        except Address.DoesNotExist:
            address = usr_factories.AddressFactory(name='Jobsite 1',
                                                   user=user,
                                                   country=Country.objects.get(id=6252001),
                                                   state=Region.objects.get(id=4736286))
            # address = usr_factories.AddressFactory(name='Jobsite 1',
            # country=Country.objects.get(id=1269750),
            #                                        state=Region.objects.get(id=1270770),
            #                                        user=user)

        return address

    def parse_csv(self, f, location):
        csv_file = csv.DictReader(open(f))
        for row in csv_file:
            group_id = row['GROUP']
            class_name = row['CLASS DESCRIPTION'].capitalize()
            group_name = row['GROUP DESCRIPTION'].capitalize()
            product_name = row['DESCRIPTION - PRINTS ON INVOICE'].capitalize()
            product_num = row['PRODUCT NUMBER']

            if group_id == 'ADD TO SYS' or not class_name:
                continue

            # category
            category, created = Category.objects.get_or_create(name=class_name, parent=None)
            subcategory = None
            if group_name:
                subcategory, created = Category.objects.get_or_create(name=group_name,
                                                                      parent=category)
            cat = subcategory or category

            # tags
            tags = []
            for i in xrange(7):
                tag = row['ALTERNATE DESCRIPTION #%s' % str(i + 1)].capitalize()
                if tag:
                    tags.append(tag)

            # attributes
            attributes = {}
            if row['MODEL']:
                attributes['model'] = row['MODEL']

            # SKU
            sku_2 = crc32(''.join(tags))  # tags crc
            sku_1 = crc32(product_name)  # product name crc
            sku = '%s%s-%s' % (product_name[:4].upper(), cat.id, sku_1 + sku_2)
            sku = sku.replace('--', '-')

            # Product
            try:
                product = Product.objects.get(user=location.user, sku=sku)
            except Product.DoesNotExist:
                try:
                    product = ProductFactory(name=product_name, category=cat, sku=sku,
                                             location=location, user=location.user, tags=tags,
                                             attributes=attributes)
                except UnicodeDecodeError:
                    continue

            InventoryFactory(product=product, serial_no=product_num, is_active=True,
                             user=location.user)

