# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0008_product_hourly_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='is_active',
            field=models.BooleanField(db_index=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_active',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=100, db_index=True),
        ),
    ]
