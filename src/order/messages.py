from django.utils.translation import ugettext as _

from common.errors import Code


ERR_NON_SHIPPABLE = _('One of the items in your cart is unable to ship to your location. Please '
                      'remove that item'), Code.ORDER + 1
ERR_INVALID_CART_USER = _('You can only order your cart'), Code.ORDER + 2
ERR_MISS_SHIPPING_KIND = _('Please select shipping kind for the item "%s"'), Code.ORDER + 3

ERR_CANCEL_ITEM_DISPATCHED = _("This item cannot be cancelled as it's been dispatched or picked "
                               "up. Please kindly raise request for return"), Code.ORDER + 4
ERR_NO_INVENTORIES = _('You cannot approve the order item until you assign the inventories'), \
                     Code.ORDER + 5

ERR_INVALID_STATUS = _("Invalid status"), Code.ORDER + 6
ERR_NOT_CHANGEABLE = _("Current status is not changeable to this status"), Code.ORDER + 7

ERR_INACTIVE_INVENTORY = _('This inventory is already occupied'), Code.ORDER + 8
