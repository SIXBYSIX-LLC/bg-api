"""
=====
Tasks
=====
"""

from django.db.models.signals import post_save

from common.dispatch import async_receiver
from .models import Message
from .notifications import email


@async_receiver(post_save, sender=Message)
def send_new_message_email(sender, **kwargs):
    """
    Sends email to user when new message is received.

    :on signal: post_save, Message
    :Async: True
    """
    message = kwargs.get('instance')
    email.send_message_email(message)
