from django.db.models.signals import pre_save

from common.dispatch import receiver
from .models import Category


@receiver(pre_save, sender=Category)
def build_hierarchy(sender, **kwargs):
    category = kwargs.get('instance')
    category.build_hierarchy()
