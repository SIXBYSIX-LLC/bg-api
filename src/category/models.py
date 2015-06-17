from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseModel, BaseManager


class CategoryManager(BaseManager):
    pass


class Category(BaseModel):
    #: Category name
    name = models.CharField(max_length=50)
    #: image
    image = models.URLField(blank=True, null=True)
    #: Parent category if any
    parent = models.ForeignKey('Category', null=True, blank=True, default=None)
    #: This holds the array of full hierarchy of the category starting from root to last child
    # element.
    hierarchy = pg_fields.ArrayField(models.IntegerField(), blank=True, null=True)

    objects = CategoryManager()

    class Meta(BaseModel.Meta):
        db_table = 'category'

    def build_hierarchy(self):
        cats = []

        cat = self
        while cat.parent is not None:
            cats.append(cat.parent.id)
            cat = cat.parent

        self.hierarchy = list(reversed(cats))
