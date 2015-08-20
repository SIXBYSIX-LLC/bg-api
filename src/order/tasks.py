from common.dispatch import async_receiver
from . import signals


@async_receiver(signals.order_confirm)
def send_order_confirmation(sender, **kwargs):
    """
    Sends order confirmation mail to buyer
    """
    order = kwargs.get('instance')
    confirmation_now = kwargs.get('now')
    order.send_confirmation_email(now=confirmation_now)


@async_receiver(signals.order_confirm)
def send_order_receive_email(sender, **kwargs):
    """
    Sends order confirmation mail to seller
    """
    order = kwargs.get('instance')
    confirmation_now = kwargs.get('now')

    for orderline in order.orderline_set.all():
        orderline.send_confirmation_email(now=confirmation_now)
