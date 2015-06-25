import factory

from common.faker import fake
from ..models import Thread, Message


class ThreadFactory(factory.DjangoModelFactory):
    class Meta:
        model = Thread

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class.objects.create_thread(*args, **kwargs)


class MessageBaseFactory(factory.DictFactory):
    text = factory.LazyAttribute(lambda x: fake.paragraphs(nb=2))


class MessageFactory(factory.DjangoModelFactory, MessageBaseFactory):
    class Meta:
        model = Message
