from django.utils.translation import ugettext as _

from common.errors import Code


ERR_INVALID_TARGET = _('Target id not found specified with target'), Code.STATIC + 1
ERR_PRODUCT_IMAGE_LIMIT = _('You can upload upto 10 images to single product'), Code.STATIC + 2
ERR_INVALID_FORMAT = '', Code.STATIC + 3
