from django.db import models


class BaseManager(models.Manager):
    pass


class BaseModel(models.Model):
    objects = BaseManager()

    class Meta:
        abstract = True
