from django.db.models.signals import post_save

from common.dispatch import async_receiver
from .models import ContactUs
from .notifications import email


@async_receiver(post_save, sender=ContactUs)
def send_autoreply(sender, **kwargs):
    contactus = kwargs.get('instance')
    email.send_autoreply_to_visitor(contactus)
