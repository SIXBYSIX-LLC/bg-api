from django.db import models, transaction
from djangofuture.contrib.postgres import fields as pg_fields
from django.conf import settings
import cloudinary.uploader

from common.models import BaseModel, BaseManager
from . import constants, messages
from common import errors
from . import errors as e


class FileManager(BaseManager):
    def upload(self, f, **kwargs):
        target = kwargs.pop('target')

        if target == constants.TARGET_PRODUCT_IMAGE:
            file_obj = self._add_to_product_image(f, **kwargs)
        elif target == constants.TARGET_CATEGORY_IMAGE:
            file_obj = self._set_category_image(f, **kwargs)

        return file_obj

    def _add_to_product_image(self, f, **kwargs):
        from catalog.models import Product

        target_id = kwargs.pop('target_id')
        user = kwargs.pop('user')
        path = '%s/product_images/%s' % (settings.STATIC_FILE_BASE, target_id)

        # Check and get if product with given target id is exists
        try:
            product = Product.objects.get(id=target_id)
            if product.images.count() > 9:
                raise e.ProductImageError(*messages.ERR_PRODUCT_IMAGE_LIMIT)
        except product.DoesNotExist:
            raise errors.ValidationError(*messages.ERR_INVALID_TARGET)

        # Upload to cloudinary
        response = cloudinary.uploader.upload_image(f, public_id=path, use_filename=True)
        meta = response.metadata

        with transaction.atomic() as t:
            file_obj = self.create(url=meta.get('secure_url'), upload_resp=meta,
                                   target=constants.TARGET_PRODUCT_IMAGE, target_id=target_id,
                                   user=user)
            product.images.add(file_obj)

        return file_obj

    def _set_category_image(self, f, **kwargs):
        from category.models import Category

        target_id = kwargs.pop('target_id')
        user = kwargs.pop('user')
        path = '%s/category_images/%s' % (settings.STATIC_FILE_BASE, target_id)

        # Check and get if product with given target id is exists
        try:
            category = Category.objects.get(id=target_id)
        except category.DoesNotExist:
            raise errors.ValidationError(*messages.ERR_INVALID_TARGET)

        # Upload to cloudinary
        response = cloudinary.uploader.upload_image(f, public_id=path, use_filename=True)
        meta = response.metadata

        with transaction.atomic() as t:
            file_obj = self.create(url=meta.get('secure_url'), upload_resp=meta,
                                   target=constants.TARGET_CATEGORY_IMAGE, target_id=target_id,
                                   user=user)
            category.image = file_obj
            category.save(update_fields=['image'])
        return file_obj


class File(BaseModel):
    TARGETS = (
        (constants.TARGET_PRODUCT_IMAGE, 'Product Image'),
        (constants.TARGET_CATEGORY_IMAGE, 'Category Image'),
    )
    #: Uploaded url
    url = models.URLField()
    #: response received from uploading service
    upload_resp = pg_fields.JSONField(blank=True, editable=False, null=True)
    #: Target model name
    target = models.CharField(choices=TARGETS, max_length=100)
    #: Target object pk
    target_id = models.CharField(max_length=10)
    user = models.ForeignKey('miniauth.User', default=None, blank=True, editable=False)

    Const = constants

    objects = FileManager()

