"""
****
Cart
****

Cart allows customers to accumulate a list of items for purchase or rent,
described metaphorically as "placing items in the shopping cart" or "add to cart."
Upon checkout, system calculates a total for the order, including shipping and handling
(i.e., postage and packing) charges and the associated taxes, as applicable.

Typical process of
purchasing or renting the item is to add them into the cart. User will be having only single cart
at a time and it'll be preserved until checkout or manual clear process.

Cart can be value of 0 if contains all rental items, so the payable amount would be 0 at the time
of checkout


Data Structure
--------------

Whole cart module is divided into three models,
``Cart`` that hold the summary of user items, shipping and billing address.
``RentalItem`` that holds the Rental items to be ordered and derived from the abstract class
``Item``.
``PurchaseItem`` that hold the items to be purchase and derived from the abstract class Item.

``RentalItem`` and ``PurchaseItem`` both are stored in their separate tables. It was my initial
decision to do so but can be stored in single table and only rental item attributes into another
(which is done in Order).


Additional Charges
------------------
If you look at the Cart model, there is a field called Additional charge. Additional charges are
all other charges that levied by the seller including sales tax, i.e. it's seller define charges.

Each additional charge can be found in `costbreakup['additional_charge']` dict with specific format
of

.. code::

    {
        unit: Either percentage or flat
        name: Human readable name like 'Sales Tax'
        value: Value of additional charge
        amt: Final amount to be added to cart total
    }


Calculating the Cart Total
--------------------------

Whenever item is added or updated in cart, ``serializer.create()`` calls the
``Cart.calculate_cost()`` which is responsible for calculating item total cost and then cart
total cost.

When item is removed, I used ``PurchaseItem.post_delete`` and ``RentalItem.post_delete`` signal
to calculate the cost but without recalculating the item cost again.

Modules
-------
"""

default_app_config = 'cart.apps.CartConfig'
