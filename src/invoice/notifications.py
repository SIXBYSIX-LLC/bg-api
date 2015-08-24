__all__ = ['email']

from django.utils import timezone

from common.notifications import BaseEmailNotification
from transaction import constants as trans_const


class EmailNotification(BaseEmailNotification):
    def send_invoice_paid(self, invoice_instance, **kwargs):
        """
        Sends order receive email to seller. The following variable will be available in the
        template
        Variables:

        * **USER_FULLNAME**
        * **USER_EMAIL**
        * **TOTAL**
        * **PAYMENT_DATE**
        * **TRANSACTION_ID**
        * **INVOICE_ID**
        """
        # Merge tags in template
        now = kwargs.pop('now', None) or timezone.now()
        instance = invoice_instance
        transaction = instance.last_transaction(trans_const.Status.SUCCESS)

        self.msg.global_merge_vars = {
            'USER_FULLNAME': instance.user.profile.fullname,
            'USER_EMAIL': instance.user.email,
            'TOTAL': instance.total,
            'PAYMENT_DATE': instance.user.profile.localtime(now),
            'TRANSACTION_ID': transaction.id if transaction else None,
            'INVOICE_ID': instance.id,
        }

        return self._send(to=[instance.user.email], template_name=self.ETPL_INVOICE_PAID)


email = EmailNotification()
