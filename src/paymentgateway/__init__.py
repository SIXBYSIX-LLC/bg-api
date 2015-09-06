"""
***************
Payment Gateway
***************
This app takes care of collecting payment from the user.

Payment gateway only collects the payment for invoice. Arbitrary payment is not possible using
this gateway.

If the invoice amount is 0, there is special payment gateway called ``Postpaid`` is designed that
mark the invoice as paid only for 0 amount invoice.

To collect actual amount, we implemented Braintree gateway and braintree's drop-in UI that give
nonce token to charge.

.. todo:: Implementing distributing the payment to seller


Module
------
"""
