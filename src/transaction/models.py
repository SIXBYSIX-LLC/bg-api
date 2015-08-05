import string
import urllib
import logging

from django.db import models, transaction
from djangofuture.contrib.postgres import fields as pg_fields
from django.utils.crypto import get_random_string

from common.models import BaseModel, DateTimeFieldMixin, BaseManager
from common import fields as ex_fields
from system import paymentgateway
from . import constants


L = logging.getLogger('bgapi.' + __name__)


class TransactionManager(BaseManager):
    def pay_invoice(self, gateway, invoice, return_url, **kwargs):
        with transaction.automic():
            # Getting payment gateway
            pg = paymentgateway.get_by_name(gateway)
            L.info('Invoice initiated transaction', extra={
                'invoice': invoice.id, 'gateway': gateway, 'return_url': return_url,
                'pg_gateway': pg.name
            })

            # Generate transaction id, mix of user id and transaction id
            _id = '%s%s%s' % (
                invoice.id, invoice.user_id,
                get_random_string(15, allowed_chars=string.ascii_uppercase + string.digits)
            )

            # Initiate the transaction
            t = self.create(
                id=_id,
                payer=invoice.user,
                invoice=invoice,
                expected_amt=invoice.total,
                using=gateway,
                return_url=return_url
            )
            L.debug('Transaction is created', extra={'transaction': t.id})

            # Call for the charge by payment gateway
            response = pg.charge(invoice, _id)
            L.debug('Charged by payment gateway', extra={
                'status': response.status, 'message': response.message,
                'redirect_url': response.redirect_url
            })

            # Redirect URL is none, which means payment is processed server side and we need to
            # redirect user to return url with status
            if response.redirect_url is None:
                # As payment is processed already, we can make transaction a success and fill the
                # necessary detail
                t.received_amt = response.received_amt
                t.status = response.status
                t.response = response.raw
                t.save(update_fields=['received_amt', 'status', 'response'])
                L.debug('Payment is processed server side and transaction is marked as %s',
                        t.status)

                # Preparing query params for return url
                q_params = urllib.urlencode({
                    'status': response.status,
                    'message': response.message,
                    'transaction_id': id
                })
                if '?' not in return_url:
                    q_params = '?' + q_params
                url = return_url + q_params
            else:
                url = response.redirect_url

            L.info('Transaction is completed', extra={'redirect_url': url})
            return url, t.id


class Transaction(BaseModel, DateTimeFieldMixin):
    #: Transaction id generated by the system
    id = models.CharField(max_length=50, primary_key=True)
    #: User who is going to pay/paid
    payer = models.ForeignKey('miniauth.User')
    #: Invoice this transaction is for
    invoice = models.ForeignKey('invoice.Invoice')
    #: Amount to be expected
    expected_amt = ex_fields.FloatField(min_value=0.0, precision=2)
    #: Amount received from payment gateway
    received_amt = ex_fields.FloatField(min_value=0.0, precision=2, null=True)
    #: Payment gateway name
    using = models.CharField(max_length=30)
    #: Status of the transaction
    status = models.CharField(max_length=30, default=constants.Status.INITIATE)
    #: Response from the payment gateway
    response = pg_fields.JSONField(default=None, null=True)
    #: Return url after successful payment
    return_url = models.URLField(null=True)

    objects = TransactionManager()

    @property
    def _gateway(self):
        """
        :return: Payment gateway object
        """
        pass

    def refund(self, amt):
        """
        Refunds the amount

        :param Float amt: Amount to be refunded
        :return Refund: Refund object
        """
