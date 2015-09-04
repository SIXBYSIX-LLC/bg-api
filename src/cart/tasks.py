"""
=====
Tasks
=====
"""
from django.db.models.signals import pre_save, post_delete

from cart.models import RentalItem, PurchaseItem
from common.dispatch import receiver


@receiver(pre_save, sender=PurchaseItem)
@receiver(pre_save, sender=RentalItem)
def is_shippable(sender, **kwargs):
    """
    Check if the item is shippable to cart location, if set it sets RentalItem.is_shippable to True

    :on signals: pre_save, PurchaseItem
    :on signals: pre_save, RentalItem
    :sync: True
    """
    rental_item = kwargs.get('instance')
    if rental_item.id:
        return

    if rental_item.shipping_method:
        rental_item.is_shippable = True


@receiver(post_delete, sender=RentalItem)
@receiver(post_delete, sender=PurchaseItem)
def update_cart_cost_on_rental_removed(sender, **kwargs):
    """
    Update cart calculation when item is removed from the cart.

    :on signals: post_delete, PurchaseItem
    :on signals: post_delete, RentalItem
    :sync: True
    """
    rental_item = kwargs.get('instance')
    rental_item.cart.calculate_cost(force_item_calculation=False)


