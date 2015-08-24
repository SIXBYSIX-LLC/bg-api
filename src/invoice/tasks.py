import logging

from celery import shared_task

from invoice.models import Invoice
from common.dispatch import async_receiver
from . import signals
from .notifications import email

L = logging.getLogger('bgapi.' + __name__)


@shared_task()
def auto_approve_invoice():
    L.info('Begins auto approving task')

    invoices = Invoice.objects.unapproved_for_days(16)

    if L.isEnabledFor(logging.DEBUG):
        L.debug('Total %d invoices found that elapsed the 15 days review period', invoices.count())

    for invoice in invoices:
        invoice.approve(force=True)


@async_receiver(signals.invoice_paid)
def send_invoice_paid_invoice(sender, **kwargs):
    instance = kwargs.get('instance')
    now = kwargs.get('now')

    if kwargs.get('force') is True:
        return

    email.send_invoice_paid(instance=instance, now=now)
