"""
*******
Inquiry
*******
This app enables the text communication between seller and buyer.
Current implementation allows user to raise inquiry about the product prior to the.

.. todo::
    * Allow inquiry for on-going contract item


Implementation
--------------
The messages are implemented based on threads. For each product only one thread is
created. More messages can be added to thread.


Read / Unread Messages
----------------------
All new messages created by user is marked as unread by default. ``Message.is_read`` attribute is
responsible to indicating read/unread.

Whenever user calls the list message API, view action will mark all the messages in current
queryset as read


Modules
-------
"""
default_app_config = 'inquiry.apps.InquiryConfig'
