"""
Categories
----------
The categories endpoint supports getting specific information about one category, subcategory, or a collection of categories.
These categories represent a main category, a subcategory, or a specific category page to load and display in the buildergiant.
Products are associated to only one leaf subcategory. These groupings give shoppers a browsing experience for locating products in marketplace.

To navigate to subcategories for product assignment, categories can be filter by its parent category.

Categories can only be created/updated by Admins only.

TODO:
    - Update product category in case of subcategory changes its parent or get a subcategory
    - Update product category to new category in case of subcategory gets deleted
"""
default_app_config = 'category.apps.CategoryConfig'
