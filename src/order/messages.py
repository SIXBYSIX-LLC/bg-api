from django.utils.translation import ugettext as _

ERR_NON_SHIPPABLE = _('One of the items in your cart is unable to ship to your location. Please '
                      'remove that item'), 7001
ERR_INVALID_CART_USER = _('You can only order your cart'), 7002
ERR_MISS_SHIPPING_KIND = _('Please select shipping kind for the item "%s"'), 7003
