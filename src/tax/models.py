from django.db import models

from common.models import BaseModel
from common import fields as ex_fields


class Tax(BaseModel):
    UNITS = (
        ('pct', 'Percentage'),
        ('flat', 'Flat'),
    )
    name = models.CharField(max_length=50, default='Tax')
    value = ex_fields.FloatField(min_value=0, max_value=9999, precision=2)
    unit = models.CharField(choices=UNITS, max_length=30)

    class Meta(BaseModel.Meta):
        abstract = True


class SalesTax(Tax):
    country = models.ForeignKey('cities.Country')
    state = models.ForeignKey('cities.Region', null=True)

    class Meta(Tax.Meta):
        unique_together = ('country', 'state')
