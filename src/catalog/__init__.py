"""
********
Catalog
********

Catalog holds the module for Products and product inventories. Seller can upload their own
product to catalog and add inventories to product.


Product
-------
Product is a item that consist of different property like name, images, description, etc... Such
item will be showcased to user to consume by either purchasing it or renting it.

Product can fall into only single leaf category (the last child). It can have multiple images.

There is only single property ``name`` is defined to name/identify the product. If you want
product to be searchable for other names as well, you can add them in ``Product.tags`` array fields

There are few standard properties defined for a product. If the product needs more attribute to
define, ``Product.attributes`` can be used.

Searching
^^^^^^^^^
For search, we use postgres' standard vector function (which can be slow) and only single method
``ProductManager.search()`` is responsible to filter the result according to search term.

.. todo::
    * Refactor to **Elasticsearch**


Inventories
-----------
Inventory defines as number product in-stock. Each product can have multiple inventory objects.
As our platform and use case is more deal with single item, intentionally I created multiple
objects for inventory rather than just a number field to Product model. This way we can keep
track of each individual machine that goes on rent and return to stock.

To simplify the bulk inventories creation, I added ``qty`` field in ``Product`` model which
implicitly create inventories while adding the product.


Modules
-------
"""

default_app_config = 'catalog.apps.CatalogConfig'
