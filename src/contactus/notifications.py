"""
=============
Notifications
=============
"""

import logging

from common.notifications import BaseEmailNotification

L = logging.getLogger('bgapi.' + __name__)


class EmailNotification(BaseEmailNotification):
    """
    Helper class to send email notification
    """

    def send_autoreply_to_visitor(self, contactus_instance):
        """
        Sends auto reply like thank you to a visitor who has generated the inquiry

        template Variables:

        * **VISITOR_NAME**: Visitor first name + last name
        * **MESSAGE**: Message, visitor just left
        """
        contactus = contactus_instance

        self.msg.global_merge_vars = {
            'VISITOR_NAME': '%s %s' % (contactus.first_name, contactus.last_name),
            'MESSAGE': contactus.message
        }

        self._send(to=[contactus.email], template_name=self.ETPL_CONTACTUS_AUTOREPLY)


email = EmailNotification()
