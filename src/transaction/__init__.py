"""
***********
Transaction
***********
This app is intended to keep track of payment transaction for the invoice.

Whenever invoice needs to be paid, new transaction instance is created and then referenced in
payment gateway. When it's created, its status is set to ``initiate`` and according to payment
gateway response, it further mark as success or fail.

Upon successful payment transaction, it also marks invoice as paid.


How it Works
------------
* Initially when invoice needs to pay, new transaction is created. While creating transaction, \
redirect url needs be given. It's something like callback url for payment status. So payment \
status and message are appended to that url and frontend can decide what do display on page based \
payment status.
* Transaction manager's pay method calls payment gateway and return redirect url and transaction \
instance.
* Redirect url can be payment gateway's hosted page to collect payment or simply same as return \
url if payment can be process on server side.

.. todo:: Refund full/partial amount


Modules
-------
"""
