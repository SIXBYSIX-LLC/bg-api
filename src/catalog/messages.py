from django.utils.translation import ugettext as _

from common.errors import Code


ERR_NOT_LEAF_CATEGORY = _('This is not leaf category. Please select the child category'), \
                        Code.CATALOG + 1
