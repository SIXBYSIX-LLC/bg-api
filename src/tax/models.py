from django.db import models

from common.models import BaseModel


class Tax(BaseModel):
    UNITS = (
        ('pct', 'Percentage'),
        ('flat', 'Flat'),
    )
    name = models.CharField(max_length=50, default='Tax')
    value = models.DecimalField(max_digits=4, decimal_places=2)
    unit = models.CharField(choices=UNITS, max_length=30)

    class Meta(BaseModel.Meta):
        abstract = True


class SalesTax(Tax):
    country = models.ForeignKey('cities.Country')
    state = models.ForeignKey('cities.Region', null=True)

    class Meta(Tax.Meta):
        unique_together = ('country', 'state')
