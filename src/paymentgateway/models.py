import braintree
import jsonpickle

from common import errors
from . import messages
from .response import ChargeResponse
from transaction.constants import Status as status_const
from system.models import Config


class PaymentGateway(object):
    """
    Base class for payment gateways. All payment gateway should inherit this class
    """

    def charge(self, invoice, transaction_ref, **kwargs):
        raise NotImplementedError

    def capture(self, transaction, **kwargs):
        raise NotImplementedError

    @staticmethod
    def to_json(obj):
        return jsonpickle.encode(obj)


class Postpaid(PaymentGateway):
    """
    Dummy gateway specially created for the 0 amount payment. 0 amount can be happen if all
    order item is for rental.
    """
    name = 'postpaid'

    def charge(self, invoice, transaction_ref, **kwargs):
        if invoice.total > 0:
            raise errors.PaymentError(*messages.ERR_INVALID_AMT)

        return ChargeResponse(
            redirect_url=None,
            received_amt=0,
            raw={},
            status=status_const.SUCCESS,
            message='Payment is successful'
        )


class Braintree(PaymentGateway):
    """
    Implementation of braintree gateway

    See: https://developers.braintreepayments.com
    """
    name = 'braintree'

    def __init__(self, *args, **kwargs):
        # Load the config
        self.config = Config.objects.get(pk=self.name).config
        # Getting environment object
        environment = getattr(braintree.Environment, self.config.pop('environment'))

        braintree.Configuration.configure(environment, **self.config)

        super(Braintree, self).__init__(*args, **kwargs)

    def generate_client_token(self):
        """
        Generates client token.
        See https://developers.braintreepayments.com/javascript+python/start/hello-client#get-a-client-token
        """
        return braintree.ClientToken.generate()

    def charge(self, invoice, transaction_ref, **kwargs):
        """
        We take simple approach to charge customer (create sale). We shall be using the
        braintree's drop-in or client SDK to get credit card or payment information then client
        SDK is responsible to generate nonce. Because it's deprecated and not PCI compliant to
        traverse the CC information directly to server

        Once the nonce is generated, it's be sent to payment endpoint and this function will be
        using that nonce for btraintree `payment_method_nonce` parameter.

        :param Invoice invoice: Invoice to be paid
        :param str transaction_ref: Transaction reference string. Usually a transaction id
        :param kwargs:
            :param dict nonce: Should contain following attributes
                :param str payment_method_nonce: Nonce received by response from braintree
        :return:
        """
        if invoice.total < 1:
            raise errors.PaymentError(*messages.ERR_INVALID_AMT)

        nonce = kwargs.pop('nonce', {})

        result = braintree.Transaction.sale({
            "amount": str(invoice.total),
            "order_id": str(invoice.id),
            "payment_method_nonce": nonce.get('payment_method_nonce'),
            "billing": self.__format_invoice_address(invoice.order.billing_address),
            "shipping": self.__format_invoice_address(invoice.order.shipping_address),
            "customer": self.__format_customer(invoice.user),
            "options": {
                "submit_for_settlement": True
            },
            "custom_fields": {
                "transaction_id": str(transaction_ref),
                "invoice_id": str(invoice.id),
                "order_id": str(invoice.order_id)
            }
        })

        return ChargeResponse(
            redirect_url=None,
            received_amt=result.transaction.amount if result.transaction else 0,
            raw=self.to_json(result),
            status=status_const.SUCCESS if result.is_success else status_const.FAIL,
            message='Payment is successful' if result.is_success else result.message
        )

    @classmethod
    def __format_invoice_address(cls, address):
        """
        Format invoice address object to dict required by braintree

        See: https://developers.braintreepayments.com/ios+python/reference/request/transaction/sale
        """
        return {
            "first_name": address.first_name,
            "last_name": address.last_name,
            "company": address.company_name,
            "street_address": address.address1,
            "extended_address": address.address2,
            "locality": address.city.name_std,
            "region": address.state.code,
            "postal_code": address.zip_code,
            "country_code_alpha2": address.country.code
        }

    @classmethod
    def __format_customer(cls, user):
        """
        Format user object to customer dict required by braintree

        See: https://developers.braintreepayments.com/ios+python/reference/request/transaction/sale
        """

        profile = user.profile

        return {
            "first_name": profile.fullname.split(' ')[0],
            "last_name": profile.fullname.split(' ')[1],
            "phone": profile.phone,
            "email": user.email
        }


def get_by_name(name):
    """
    Return the payment gateway object

    :param str name: Payment gateway name
    :return PaymentGateway:
    :raise PaymentError:
    """
    pgs = [Postpaid, Braintree]
    for pg in pgs:
        if pg.name == name.lower().strip():
            return pg()

    raise errors.PaymentError(*messages.ERR_INVALID_PG_NAME)
