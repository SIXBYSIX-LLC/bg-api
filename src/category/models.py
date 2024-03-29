"""
======
Models
======
"""

from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseModel, BaseManager


class CategoryManager(BaseManager):
    pass


class Category(BaseModel):
    """
    Class to store categories

    .. note:: Can not be delete
    """
    #: Category name
    name = models.CharField(max_length=50)
    #: image
    image = models.ForeignKey('static.File', null=True, blank=True, default=None,
                              on_delete=models.SET_NULL)
    #: Parent category if any
    parent = models.ForeignKey('Category', null=True, blank=True, default=None)
    #: This holds the array of full hierarchy of the category starting from root to last child
    #: element.
    hierarchy = pg_fields.ArrayField(models.IntegerField(), blank=True, null=True)

    objects = CategoryManager()

    class Meta(BaseModel.Meta):
        db_table = 'category'
        unique_together = ('name', 'parent')

    def build_hierarchy(self):
        """
        Builds and saves category hierarchy from parents to child
        """
        cats = []

        cat = self
        while cat.parent is not None:
            cats.append(cat.parent.id)
            cat = cat.parent

        self.hierarchy = list(reversed(cats))
