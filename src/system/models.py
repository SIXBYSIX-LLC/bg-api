"""
======
Models
======
"""

from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseModel, DateTimeFieldMixin, BaseManager


class ConfigManager(BaseManager):
    """
    Manager class for config
    """
    def get_by_natural_key(self, k):
        """
        Returns config dict by key
        """
        try:
            return self.get(id=k).config
        except Config.DoesNotExist:
            return {}

    def coreconf(self):
        """
        Shortcut method to retrieve core config dict
        """
        return self.get_by_natural_key('core')


class Config(BaseModel, DateTimeFieldMixin):
    """
    Class to store system wide configs

    .. note:: Cannot be deleted
    """
    id = models.CharField(primary_key=True, max_length=50)
    config = pg_fields.JSONField(default={})

    objects = ConfigManager()
