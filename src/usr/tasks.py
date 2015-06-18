from django.db.models.signals import post_save

from common.dispatch import async_receiver, receiver
from group.models import Group
from . import signals, models


@async_receiver(signals.user_registered)
def send_email_verification(sender, **kwargs):
    user = kwargs.get('instance')
    user.send_email_verification()


@receiver(post_save, sender=models.Profile)
def assign_group(sender, **kwargs):
    if kwargs.get('created', False) is False:
        return
    profile = kwargs['instance']
    profile.groups.add(Group.objects.get_or_create(name='User'))
