from django.utils.translation import ugettext as _

ERR_RENT_INVALID_PRODUCT = _('This product cannot be add as rental product'), 6001
ERR_INVALID_END_DATE = _('End date must be greater than minimum contract period'), 6002

ERR_PURCHASE_INVALID_PRODUCT = _('This product cannot be add as purchase item'), 6011

ERR_CHKT_CART_INACTIVE = _('Cannot checkout inactivated cart'), 6021
ERR_CHKT_NO_SHIPPING_ADDR = _('Shipping address cannot be blank'), 6022
ERR_CHKT_NO_BILLING_ADDR = _('Billing address cannot be blank'), 6023
ERR_CHKT_NO_ITEM = _('Cannot checkout empty cart'), 6024
