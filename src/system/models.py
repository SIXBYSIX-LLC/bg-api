from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseModel, DateTimeFieldMixin, BaseManager


class ConfigManager(BaseManager):
    def get_by_natural_key(self, k):
        try:
            return self.get(id=k).config
        except Config.DoesNotExist:
            return {}

    def coreconf(self):
        return self.get_by_natural_key('core')


class Config(BaseModel, DateTimeFieldMixin):
    """
    (Cannot be deleted)
    """
    id = models.CharField(primary_key=True, max_length=50)
    config = pg_fields.JSONField(default={})

    objects = ConfigManager()
