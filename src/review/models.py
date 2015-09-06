"""
======
Models
======
"""

from django.db import models

from common.models import BaseModel, BaseManager
from common import fields as ex_fields, helper, errors
from . import constants, messages


class OrderItemManager(BaseManager):
    """
    Manager class for Order Item
    """
    def create_review(self, **kwargs):
        """
        Creates review from order item and also decided who either buyer/seller is writing the
        review.
        """
        order_item = kwargs.get('order_item')
        to_user = order_item.orderline.user
        user = kwargs.get('user')
        reviewer = constants.Reviewer.BUYER
        product_id = order_item.detail.get('id')

        # if user is item owner, it's seller writing the review about user
        if user.id == order_item.detail.get('user'):
            reviewer = constants.Reviewer.SELLER
            to_user = order_item.user

        model = OrderItem(to_user=to_user, reviewer=reviewer, product_id=product_id, **kwargs)
        model.full_clean()
        model.save()

        return model


class OrderItem(BaseModel):
    """
    Class to store review for order item that buyer/seller writes to each other
    """
    REVIEWER = helper.prop2pair(constants.Reviewer)

    #: Review writer
    user = models.ForeignKey('miniauth.User', related_name='+', editable=False, default=None)
    to_user = models.ForeignKey('miniauth.User', related_name='+', editable=False)
    reviewer = models.CharField(choices=REVIEWER, max_length=30, editable=False)
    #: Catalog product as generic key
    product = models.ForeignKey('catalog.Product', editable=False)
    #: The order item which this review is for
    order_item = models.ForeignKey('order.Item')
    #: Comment
    comment = models.CharField(max_length=1000, default='')
    #: Rating, max 5 star
    rating = ex_fields.SmallIntegerField(min_value=1, max_value=5)

    objects = OrderItemManager()

    class Meta(BaseModel.Meta):
        unique_together = ('user', 'order_item')

    def clean(self):
        # Validates if writer should be one of buyer or seller
        if self.user not in [self.order_item.user, self.order_item.orderline.user]:
            raise errors.ReviewError(*messages.ERR_USER_NOT_VALID)

