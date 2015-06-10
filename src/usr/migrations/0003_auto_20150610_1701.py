# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('usr', '0002_auto_20150609_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(max_length=30, verbose_name='Phone number'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='store_name',
            field=models.CharField(max_length=50, unique=True, null=True, verbose_name='Store name',
                                   blank=True),
        ),
    ]
