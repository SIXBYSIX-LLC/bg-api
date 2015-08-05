from django.db import models
from djangofuture.contrib.postgres import fields as pg_fields

from common.models import BaseModel, DateTimeFieldMixin


class Config(BaseModel, DateTimeFieldMixin):
    id = models.CharField(primary_key=True, max_length=50)
    config = pg_fields.JSONField(default={})
