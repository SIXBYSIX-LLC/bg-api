"""
Models
======
Provides base models for other django.model subclass
"""
from django.db import models


class BaseManager(models.Manager):
    pass


class BaseModel(models.Model):
    """
    Adds default permissions and some common methods
    *Always use this class instead of django.db.models.Model*
    """
    objects = BaseManager()

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        abstract = True
