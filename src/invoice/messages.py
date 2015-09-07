from django.utils.translation import ugettext as _

from common.errors import Code


ERR_ITEM_EDIT = _('You have already approved the invoice hence cannot be edited'), Code.INVOICE + 1
ERR_TRANSACTION_CONFIRM = _('Transaction is pending success hence cannot be marked as paid'), \
                          Code.INVOICE + 2
ERR_APPROVE_INVOICE = _('Not all invoiceline is approved'), Code.INVOICE + 3
