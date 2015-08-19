import logging

from celery import shared_task
from django.utils import timezone

from invoice.models import Invoice

L = logging.getLogger('bgapi.' + __name__)


@shared_task()
def auto_approve_invoice():
    L.info('Begins auto approving task')

    invoices = Invoice.objects.filter(
        is_approve=False, date_created_at__lte=timezone.now() - timezone.timedelta(days=16)
    )

    if L.isEnabledFor(logging.DEBUG):
        L.debug('Total %d invoices found that elapsed the 15 days review period', invoices.count())

    for invoice in invoices:
        invoice.approve(force=True)
