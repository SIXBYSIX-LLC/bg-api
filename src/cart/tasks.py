from django.db.models.signals import pre_save, post_save, post_delete

from cart.models import RentalItem, Cart
from common.dispatch import receiver


@receiver(pre_save, sender=RentalItem)
def is_shippable(sender, **kwargs):
    """
    Check if the item is shippable to cart location, if set it sets RentalItem.is_shippable to True
    """
    rental_item = kwargs.get('instance')
    if rental_item.id:
        return

    if rental_item.shipping_method:
        rental_item.is_shippable = True


@receiver(pre_save, sender=RentalItem)
def update_cost(sender, **kwargs):
    rental_item = kwargs.get('instance')
    rental_item.calculate_cost()


@receiver(post_save, sender=RentalItem)
def update_cart_cost_on_rental_update(sender, **kwargs):
    rental_item = kwargs.get('instance')
    rental_item.cart.calculate_cost()


@receiver(post_delete, sender=RentalItem)
def update_cart_cost_on_rental_removed(sender, **kwargs):
    rental_item = kwargs.get('instance')
    rental_item.cart.calculate_cost()


@receiver(pre_save, sender=Cart)
def update_cart_cost_on_cart_update(sender, **kwargs):
    cart = kwargs.get('instance')
    if not cart.id:
        return
    cart.calculate_cost()

