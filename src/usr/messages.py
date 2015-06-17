from django.utils.translation import ugettext as _

ERR_OLD_PWD = _('Old password is incorrect'), 1002
ERR_EMAIL_NOT_EXISTS = _('Email does not exists'), 1003
ERR_EMAIL_PW_KEY_MISMATCH = _('Password reset key with email is mismatched'), 1004
ERR_PW_RESET_KEY_USED = _('Password reset key is invalidated. Please try resetting password '
                          'again'), 1005
ERR_INVALID_EMAIL_KEY = _('Email verification key in invalid'), 1006
ERR_INVALID_ZIP_CODE = _('Invalid zip code or zip code does not belong to selected country'), 2001
