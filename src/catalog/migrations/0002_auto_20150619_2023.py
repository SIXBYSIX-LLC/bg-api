# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='daily_price',
            field=models.DecimalField(max_digits=10, decimal_places=2,
                                      validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='monthly_price',
            field=models.DecimalField(max_digits=10, decimal_places=2,
                                      validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='sell_price',
            field=models.DecimalField(max_digits=10, decimal_places=2,
                                      validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='user',
            field=models.ForeignKey(default=None, blank=True, editable=False,
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='product',
            name='weekly_price',
            field=models.DecimalField(max_digits=10, decimal_places=2,
                                      validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
