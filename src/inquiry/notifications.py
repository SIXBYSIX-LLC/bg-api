__all__ = ['email']

import logging

from common.notifications import BaseEmailNotification

L = logging.getLogger('bgapi.' + __name__)


class EmailNotification(BaseEmailNotification):
    def send_message_email(self, message_instance):
        """
        Sends message notification to receiver. The following variable will be available in the
        template Variables:

        * **SENDER_NAME**: Order Confirmation date
        * **SENDER_EMAIL**: Order Confirmation date
        * **RECEIVER_NAME**: Order Confirmation date
        * **RECEIVER_EMAIL**: Order Confirmation date
        * **TEXT**: Order Confirmation date
        * **THREAD_ID**:
        * **MESSAGE_ID**:
        * **SUBJECT**:
        * **ITEM**:
            * **NAME**
            * **DESCRIPTION**
            * **IMAGE**
        """
        message = message_instance
        sender = message.user
        if message.user == message.thread.user:
            receiver = message.thread.to_user
        else:
            receiver = message.thread.user

        product = None
        if message.thread.product:
            product = {
                'NAME': message.thread.product.name,
                'DESCRIPTION': message.thread.product.description,
                'IMAGE': message.thread.product.image
            }

        # Merge tags in template
        self.msg.global_merge_vars = {
            'SENDER_NAME': sender.profile.fullname,
            'SENDER_EMAIL': sender.email,
            'RECEIVER_NAME': receiver.profile.fullname,
            'RECEIVER_EMAIL': receiver.email,
            'TEXT': message.text,
            'THREAD_ID': message.thread_id,
            'MESSAGE_ID': message.id,
            'SUBJECT': message.thread.subject,
            'CREATED_AT': receiver.profile.localtime(message.date_created_at),
            'PRODUCT': product
        }

        return self._send(to=[receiver.email], template_name=self.ETPL_INQUIRY_MSG)


email = EmailNotification()
