"""
======
Models
======
"""

from django.db import models

from common.models import BaseModel, BaseManager, DateTimeFieldMixin


class ThreadManager(BaseManager):
    """
    Thread manager class
    """

    def create_thread(self, **kwargs):
        """
        Helper method to create thread along with the message if text is passed as keyword argument.

        :param kwargs:
            :text: (optional,str) String used to create message
            :subject: (str) Subject of the inquiry
        """
        text = kwargs.pop('text', None)
        product = kwargs.get('product')
        kwargs['subject'] = 'Inquiry about %s' % product.name
        kwargs['to_user'] = product.user

        thread, created = self.get_or_create(**kwargs)
        if text:
            Message.objects.create(thread=thread, text=text, user=kwargs['user'])
            thread.text = text
        return thread


class Thread(BaseModel, DateTimeFieldMixin):
    """
    Class for storing thread information

    .. note:: Can not be deleted
    """
    #: Related product to be inquired
    product = models.ForeignKey('catalog.Product', null=True, default=None, blank=True)
    #: Subject, but it'll auto generated from first message
    subject = models.CharField(max_length=100, default=None, blank=True, editable=False)
    to_user = models.ForeignKey('miniauth.User', related_name='reply_threads', editable=False)
    #: Thread initiator
    user = models.ForeignKey('miniauth.User', editable=False)

    objects = ThreadManager()


class Message(BaseModel, DateTimeFieldMixin):
    """
    Class for storing messages

    .. note:: Can not be deleted
    """
    #: Message thread
    thread = models.ForeignKey('Thread')
    #: Message text
    text = models.CharField(max_length=1000)
    #: is message read by the user
    is_read = models.BooleanField(default=False)
    #: User who is creating the message
    user = models.ForeignKey('miniauth.User', editable=False)
