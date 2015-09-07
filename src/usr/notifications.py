"""
=============
Notifications
=============
"""

import logging

from django.conf import settings

from common.notifications import BaseEmailNotification
from common import errors

L = logging.getLogger('bgapi.' + __name__)


class EmailNotification(BaseEmailNotification):
    """
    Helper class to send email notification
    """
    def send_verification(self, user_instance):
        """
        Sends email address verification email. The following variable will be available in the
        template

        Variables:

        * **VERIFICATION_KEY**: Verification key
        * **USER_EMAIL**: User email address
        * **FULL_NAME**: Username
        * **WEB_DOMAIN**: Website domain name
        """
        if self.is_email_verified is True:
            raise errors.ValidationError('Email address is already verified')

        # Merge tags in template
        self.msg.global_merge_vars = {
            'VERIFICATION_KEY': user_instance.unverified_email_key,
            'USER_EMAIL': user_instance.email,
            'FULL_NAME': user_instance.fullname,
            'WEB_DOMAIN': settings.WEB_DOMAIN
        }

        return self._send(to=[user_instance.email], template_name=self.ETPL_VERIFICATION)

    def send_welcome_email(self, user_instance):
        """
        Sends email address verification email. The following variable will be available in the
        template

        Variables:

        * **USER_EMAIL**: User email address
        * **FULL_NAME**: Username
        * **WEB_DOMAIN**: Website domain name
        """
        # Merge tags in template
        self.msg.global_merge_vars = {
            'USER_EMAIL': user_instance.email,
            'FULL_NAME': user_instance.fullname,
            'WEB_DOMAIN': settings.WEB_DOMAIN
        }

        return self._send(to=[user_instance.email], template_name=self.ETPL_WELCOME)


email = EmailNotification()
