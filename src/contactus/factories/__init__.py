import factory

from common.faker import fake


class ContactusBaseFactory(factory.DictFactory):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    zip_code = fake.postalcode()
    message = fake.paragraphs()

