from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models

from common.models import BaseModel, BaseManager, DateTimeFieldMixin


class ThreadManager(BaseManager):
    def create_thread(self, **kwargs):
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
    (Can not be deleted)
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
    (Can not be deleted)
    """
    #: Message thread
    thread = models.ForeignKey('Thread')
    #: Message text
    text = models.CharField(max_length=1000)
    #: is message read by the user
    is_read = models.BooleanField(default=False)
    #: User who is creating the message
    user = models.ForeignKey('miniauth.User', editable=False)

    def send_message_email(self):
        """
        Sends message notification to receiver. The following variable will be available in the
        template Variables:
    
        * **SENDER_NAME**: Order Confirmation date
        * **SENDER_EMAIL**: Order Confirmation date
        * **RECEIVER_NAME**: Order Confirmation date
        * **RECEIVER_EMAIL**: Order Confirmation date
        * **TEXT**: Order Confirmation date
        * **THREAD_ID**:
        * **MESSAGE_ID**:
        * **SUBJECT**:
        * **ITEM**:
            * **NAME**
            * **DESCRIPTION**
            * **IMAGE**
        """

        sender = self.user
        if self.user == self.thread.user:
            receiver = self.thread.to_user
        else:
            receiver = self.thread.user

        msg = EmailMessage(to=[receiver.email])
        msg.template_name = settings.ETPL_INQUIRY_MSG

        product = None
        if self.thread.product:
            product = {
                'NAME': self.thread.product.name,
                'DESCRIPTION': self.thread.product.description,
                'IMAGE': self.thread.product.image
            }

        # Merge tags in template
        msg.global_merge_vars = {
            'SENDER_NAME': sender.profile.fullname,
            'SENDER_EMAIL': sender.email,
            'RECEIVER_NAME': receiver.profile.fullname,
            'RECEIVER_EMAIL': receiver.email,
            'TEXT': self.text,
            'THREAD_ID': self.thread_id,
            'MESSAGE_ID': self.id,
            'SUBJECT': self.thread.subject,
            'CREATED_AT': receiver.profile.localtime(self.date_created_at),
            'PRODUCT': product
        }
        # User templates subject and from address
        msg.use_template_subject = True
        msg.use_template_from = True
        # Send it right away
        msg.send()

        return True
