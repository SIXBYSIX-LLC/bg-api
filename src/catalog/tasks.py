"""
=====
Tasks
=====
"""
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify
from django.utils import timezone

from common.dispatch import receiver
from .models import Product


@receiver(pre_save, sender=Product)
def assign_sku(sender, **kwargs):
    """
    Assign SKU to product object is it's received as blank. It's composed of

    - Category id
    - First 3 characters of product name
    - User id
    - Timestamp in second

    :on signal: pre_save, Product
    :sync: True
    """
    product = kwargs.get('instance')

    if not product.sku:
        slug = slugify(product.name).replace('-', '').upper()[:3]
        product.sku = '%s%s%s%s' % (
            product.category_id, slug, product.user_id, timezone.now().strftime('%s')
        )
