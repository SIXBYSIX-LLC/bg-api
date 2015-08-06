from django.utils.translation import ugettext as _

ERR_NON_SHIPPABLE = _('One of the items in your cart is unable to ship to your location. Please '
                      'remove that item'), 7001
ERR_INVALID_CART_USER = _('You can only order your cart'), 7002
ERR_MISS_SHIPPING_KIND = _('Please select shipping kind for the item "%s"'), 7003

ERR_CANCEL_ITEM_DISPATCHED = _("This item cannot be cancelled as it's been dispatched or picked "
                               "up. Please kindly raise request for return"), 7101
ERR_NO_INVENTORIES = _('You cannot approve the order item until you assign the inventories'), 7102

ERR_INVALID_STATUS = _("Invalid status"), 7201
ERR_NOT_CHANGEABLE = _("Current status is not changeable to this status"), 7202

ERR_INACTIVE_INVENTORY = _('This inventory is already occupied'), 7301
