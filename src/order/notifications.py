__all__ = ['email']

import logging

from django.utils import timezone

from common.notifications import BaseEmailNotification

L = logging.getLogger('bgapi.' + __name__)


class EmailNotification(BaseEmailNotification):
    def send_confirmation_email_to_buyer(self, order_instance, **kwargs):
        """
        Sends order confirmation email. The following variable will be available in the template
        Variables:

        * **CONFIRM_DATE**: Order Confirmation date
        * **SHIPPING_ADDRESS**:
            * **FIRST_NAME**
            * **LAST_NAME**
            * **ADDRESS1**
            * **ADDRESS2**
            * **ZIP_CODE**
            * **CITY**
            * **STATE**
            * **COUNTRY**
            * **PHONE**
        * **FULL_NAME**: Buyer's full name
        * **ORDER_ID**: Order id
        * **PAYMENT_METHOD**: Payment method name
        * **TOTAL**: Total order amount
        * **SUBTOTAL**: Subtotal order amount
        * **ITEMS**:
            * **NAME**
            * **PRICE**
            * **QUANTITY**
            * **SHIPPING_CHARGE**
            * **ADDITIONAL_CHARGE**
            * **TOTAL**
            * **PAID_ON**
            * **SHIPPING_METHOD**
            * **ORDER_FOR**
            * **SHIPPING_KIND**
        """
        order = order_instance
        # Merge tags in template
        now = kwargs.pop('now', None) or timezone.now()
        vars_items = []
        for item in order.item_set.all():
            vars_item = {
                'NAME': item.detail.get('name'),
                'PRICE': item.subtotal,
                'IMAGE': item.detail.images[0]['url'] if item.detail.images else None,
                'QUANTITY': item.qty,
                'SHIPPING_CHARGE': item.shipping_charge,
                'ADDITIONAL_CHARGE': item.additional_charge,
                'TOTAL': item.total,
                'PAID_ON': now,
                'SHIPPING_METHOD': item.shipping_method.name if item.shipping_method else None,
                'SHIPPING_KIND': item.shipping_kind,
                # 'ORDER_FOR': 'purchase' if not item.rentalitem else 'rental'
            }
            vars_items.append(vars_item)

        self.msg.global_merge_vars = {
            'FULL_NAME': order.user.profile.fullname,
            'CONFIRM_DATE': now,
            'ORDER_ID': order.id,
            'TOTAL': order.total,
            'SUBTOTAL': order.subtotal,

            # 'PAYMENT_METHOD': self.subtotal,
            'SHIPPING_ADDRESS': {
                'FIRST_NAME': order.shipping_address.first_name,
                'LAST_NAME': order.shipping_address.last_name,
                'ADDRESS1': order.shipping_address.address1,
                'ADDRESS2': order.shipping_address.address2,
                'ZIP_CODE': order.shipping_address.zip_code,
                'CITY': order.shipping_address.city.name_std,
                'STATE': order.shipping_address.state.name_std,
                'COUNTRY': order.shipping_address.country.name,
                'PHONE': order.shipping_address.phone
            },
            'ITEMS': vars_items
        }

        return self._send(to=[self.user.email], template_name=self.ETPL_ORDER_CONFIRM)

    def send_confirmation_email_toseller(self, orderline_instance, **kwargs):
        """
        Sends order receive email to seller. The following variable will be available in the
        template
        Variables:

        * **CONFIRM_DATE**: Order Confirmation date
        * **SHIPPING_ADDRESS**:
            * **FIRST_NAME**
            * **LAST_NAME**
            * **ADDRESS1**
            * **ADDRESS2**
            * **ZIP_CODE**
            * **CITY**
            * **STATE**
            * **COUNTRY**
            * **PHONE**
        * **FULL_NAME**: Buyer's full name
        * **ORDER_ID**: Order id
        * **PAYMENT_METHOD**: Payment method name
        * **TOTAL**: Total order amount
        * **SUBTOTAL**: Subtotal order amount
        * **ITEMS**:
            * **NAME**
            * **PRICE**
            * **QUANTITY**
            * **SHIPPING_CHARGE**
            * **ADDITIONAL_CHARGE**
            * **TOTAL**
            * **PAID_ON**
            * **SHIPPING_METHOD**
            * **ORDER_FOR**
            * **SHIPPING_KIND**
        """
        orderline = orderline_instance
        # Merge tags in template
        now = kwargs.pop('now', None) or timezone.now()
        vars_items = []
        for item in orderline.item_set.all():
            vars_item = {
                'NAME': item.detail.get('name'),
                'PRICE': item.subtotal,
                'QUANTITY': item.qty,
                'SHIPPING_CHARGE': item.shipping_charge,
                'ADDITIONAL_CHARGE': item.additional_charge,
                'TOTAL': item.total,
                'PAID_ON': now,
                'SHIPPING_METHOD': item.shipping_method.name if item.shipping_method else None,
                'SHIPPING_KIND': item.shipping_kind,
                # 'ORDER_FOR': 'purchase' if not item.rentalitem else 'rental'
            }
            vars_items.append(vars_item)

        shipping_address = orderline.order.shipping_address

        self.msg.global_merge_vars = {
            'FULL_NAME': orderline.user.profile.fullname,
            'CONFIRM_DATE': now,
            'ORDER_ID': orderline.order_id,
            'ORDERLINE_ID': orderline.id,
            'TOTAL': orderline.total,
            'SUBTOTAL': orderline.subtotal,

            # 'PAYMENT_METHOD': self.subtotal,
            'SHIPPING_ADDRESS': {
                'FIRST_NAME': shipping_address.first_name,
                'LAST_NAME': shipping_address.last_name,
                'ADDRESS1': shipping_address.address1,
                'ADDRESS2': shipping_address.address2,
                'ZIP_CODE': shipping_address.zip_code,
                'CITY': shipping_address.city.name_std,
                'STATE': shipping_address.state.name_std,
                'COUNTRY': shipping_address.country.name,
                'PHONE': shipping_address.phone
            },
            'ITEMS': vars_items

        }

        return self._send(to=[self.user.email], template_name=self.ETPL_ORDER_CONFIRM)


email = EmailNotification()
