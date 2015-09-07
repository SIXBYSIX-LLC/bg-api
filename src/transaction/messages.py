from django.utils.translation import ugettext as _

from common.errors import Code


ERR_NO_APPROVE = _('Cannot pay unapproved invoice'), Code.TRANSACTION + 1
