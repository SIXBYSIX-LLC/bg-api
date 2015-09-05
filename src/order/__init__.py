"""
*****
Order
*****
Order is a collection of rental/purchase items user has availed through the checkout process.
As soon as order is created (using checkout process), the invoice will be generated of payable
amount. User should pay the invoice in order to confirm the order.


Data Structure
--------------
There is a Order class to hold summary of order.

To store the items, there is Item class to hold common information for Purchase and Rental Items.
RentalItem class stores only rental related information. PurchaseItem class is kind a helper class.

Orderline class has same characteristic as order but it contains items only from single sellers.
So for each seller for all items, there is a orderline associated with the order.


Processing the Order
--------------------
Always individual item can be processed not the whole order.
To process the order, seller will basically change the status of the item in system. Each status
can be changeable to specific set of statuses (see ``Status`` class).

As soon as buyer pay the invoice, system will put the status ``confirm``. Before processing it
further seller needs to assign inventory to item as much as the item quantity. System will
automatically mark assigned inventory to unavailable.


Modules
-------
"""
default_app_config = 'order.apps.OrderConfig'
