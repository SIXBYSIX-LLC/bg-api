from common.dispatch import async_receiver, receiver
from . import signals


@async_receiver(signals.reset_password_request)
def send_email_verification(sender, **kwargs):
    print 'send mail verification by celery'


@receiver(signals.reset_password_request)
def send_email_verification(sender, **kwargs):
    print 'send mail verification by rec'


