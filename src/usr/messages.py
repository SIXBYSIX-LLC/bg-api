from django.utils.translation import ugettext as _

from common.errors import Code


ERR_OLD_PWD = _('Old password is incorrect'), Code.USR + 1
ERR_EMAIL_NOT_EXISTS = _('Email does not exists'), Code.USR + 2
ERR_EMAIL_PW_KEY_MISMATCH = _('Password reset key with email is mismatched'), Code.USR + 3
ERR_PW_RESET_KEY_USED = _('Password reset key is invalidated. Please try resetting password '
                          'again'), Code.USR + 4
ERR_INVALID_EMAIL_KEY = _('Email verification key in invalid'), Code.USR + 5
ERR_INVALID_ZIP_CODE = _('Invalid zip code or zip code does not belong to selected country'), \
                       Code.USR + 6
