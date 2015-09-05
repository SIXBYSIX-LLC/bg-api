"""
=====
Tasks
=====
"""
import logging

from celery import shared_task

from invoice.models import Invoice, InvoiceLine
from common.dispatch import async_receiver
from . import signals
from .notifications import email

L = logging.getLogger('bgapi.' + __name__)


@shared_task()
def auto_approve_invoice():
    """
    Approve invoices if approval is pending for more than 15 days

    :scheduled: Every day
    """
    L.info('Begins auto approving task')

    invoices = Invoice.objects.unapproved_for_days(16)

    if L.isEnabledFor(logging.DEBUG):
        L.debug('Total %d invoices found that elapsed the 15 days review period', invoices.count())

    for invoice in invoices:
        invoice.approve(force=True)
        email.send_auto_approved(invoice)


@shared_task()
def approve_reminder():
    """
    Remind seller to review and approve the newly generated invoice

    :scheduled: Every 3 days
    """
    invoicelines = InvoiceLine.objects.filter(is_approve=False)
    for invoiceline in invoicelines:
        email.send_review_reminder(invoiceline)


@async_receiver(signals.invoice_paid)
def send_invoice_paid_invoice(sender, **kwargs):
    instance = kwargs.get('instance')
    now = kwargs.get('now')

    if kwargs.get('force') is True:
        return

    email.send_invoice_paid(instance=instance, now=now)


@async_receiver(signals.new_invoice_generated)
def send_invoice_paid(sender, **kwargs):
    instance = kwargs.get('instance')

    if instance.is_for_order is True:
        L.info('New invoice is of order so not sending notification to seller as it is already '
               'approved')
        return

    email.send_invoice_generate(instance=instance)


@async_receiver(signals.post_invoice_approve)
def send_invoice_approve(sender, **kwargs):
    instance = kwargs.get('instance')

    if kwargs.get('force') is True:
        L.info('Invoice is approved forcefully, hence not triggering the email notification')
        return

    email.send_approved(instance=instance)
