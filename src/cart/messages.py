from django.utils.translation import ugettext as _

from common.errors import Code


ERR_RENT_INVALID_PRODUCT = _('This product cannot be add as rental product'), Code.CART + 1
ERR_INVALID_END_DATE = _('End date must be greater than minimum contract period'), Code.CART + 2
ERR_INVALID_START_DATE = _('Start date must be %s day(s) ahead from now'), Code.CART + 8

ERR_PURCHASE_INVALID_PRODUCT = _('This product cannot be add as purchase item'), Code.CART + 3

ERR_CHKT_CART_INACTIVE = _('Cannot checkout inactivated cart'), Code.CART + 4
ERR_CHKT_NO_SHIPPING_ADDR = _('Shipping address cannot be blank'), Code.CART + 5
ERR_CHKT_NO_BILLING_ADDR = _('Billing address cannot be blank'), Code.CART + 6
ERR_CHKT_NO_ITEM = _('Cannot checkout empty cart'), Code.CART + 7
