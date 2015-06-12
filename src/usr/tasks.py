from common.dispatch import async_receiver
from . import signals


@async_receiver(signals.user_registered)
def send_email_verification(sender, **kwargs):
    user = kwargs.get('instance')
    user.send_email_verification()
