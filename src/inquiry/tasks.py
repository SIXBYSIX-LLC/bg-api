from django.db.models.signals import post_save

from common.dispatch import async_receiver
from .models import Message


@async_receiver(post_save, sender=Message)
def send_new_message_email(sender, **kwargs):
    message = kwargs.get('instance')
    message.send_message_email()
