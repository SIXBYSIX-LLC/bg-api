from django.utils.translation import ugettext as _

from common.errors import Code


ERR_INVALID_PG_NAME = _('Invalid payment gateway name'), Code.PAYMENTGATEWAY + 1
ERR_INVALID_AMT = _('Then invoice cannot be paid with this payment gateway'), \
                  Code.PAYMENTGATEWAY + 2
