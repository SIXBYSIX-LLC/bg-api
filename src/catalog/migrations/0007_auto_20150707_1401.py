# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0006_auto_20150702_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True,
                                                            base_field=models.CharField(
                                                                max_length=100), blank=True),
        ),
    ]
