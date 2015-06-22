from django.db.models.signals import post_save

from common.dispatch import async_receiver, receiver
from group.models import Group
from . import signals, models


@async_receiver(signals.user_registered)
def send_email_verification(sender, **kwargs):
    """
    Sends email for email verification to user
    """
    user = kwargs.get('instance')
    user.send_email_verification()


@receiver(post_save, sender=models.Profile)
def assign_group(sender, **kwargs):
    """
    Assign default group to user.

    TODO:
        Exclude member user to assign group
    """
    profile = kwargs['instance']

    if kwargs.get('created', False) is False or not profile.parent:
        return

    # Assign group only if creator belongs to Device group. Otherwise all the users that either
    # registered them selves or created by other user will by default be into User group and we
    # don't want that because if sub-user will have User group by default he can create another
    # user so we leave that to creator if he wants to add new user to User group
    if profile.parent.groups.filter(name='Device').exists():
        profile.groups.add(Group.objects.get_or_create(name='User')[0])
