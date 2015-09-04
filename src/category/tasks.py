"""
=====
Tasks
=====
"""

from django.db.models.signals import pre_save

from common.dispatch import receiver
from .models import Category


@receiver(pre_save, sender=Category)
def build_hierarchy(sender, **kwargs):
    """
    Proxy for ``Category.build_hierarchy()``

    :on signal: pre_save, Category
    :sync: True
    """
    category = kwargs.get('instance')
    category.build_hierarchy()
