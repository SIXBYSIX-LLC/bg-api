from common.dispatch import async_receiver
from . import signals


@async_receiver(signals.order_confirm)
def send_email_verification(sender, **kwargs):
    """
    Sends email for email verification to user
    """
    order = kwargs.get('instance')
    confirmation_now = kwargs.get('now')
    order.send_confirmation_email(now=confirmation_now)
