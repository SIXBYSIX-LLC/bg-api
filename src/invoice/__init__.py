"""
*******
Invoice
*******
This app takes care of generating invoice for orders and on-going rental contract. In-order to
confirm the order user has to pay the invoice.

Every purchase in the system raises the invoice and always invoice will be paid. No direct
payment for order is implemented. This is done to make payment flow consistent across the system.

Invoice consists of items.


Invoiceline
-----------
Invoiceline is nothing but the sub-invoice and contains the items from unique seller from whole
invoice, i.e. it's invoice which items are grouped by seller.

The aim of this class is to make isolation between items that belongs to single seller so other
seller can't see the items from other sellers. And each such invoices can be reviewed by the
seller before presenting full invoice to buyer.


Order Invoice
-------------
Whenever order is placed, new invoice is generated with ``Invoice.is_for_order=True``.

If all the items in order are rental item, invoice amount will be 0. Although invoice has to be
paid but using dummy payment gateway specially designed for this case.


Rental Invoice
--------------
At the end of the contract period or every 28 days from the order placed (whichever is earlier),
new invoice will be generated. Such invoice are marked as under reviewed using
``Invoice.is_approve=False``.

Seller will be having 15 days to review and update the Invoiceline and can mark as approve. If
seller failed to approved the invoiceline, the system will automatically mark them approve. The
``tasks.auto_approve_invoice()`` is schedule to perform such activity daily.


PDF
---
I used `wkhtmltopdf` tool to generate PDF. It's small utility that that converts HTML to PDF


Modules
-------
"""
default_app_config = 'invoice.apps.InvoiceConfig'
