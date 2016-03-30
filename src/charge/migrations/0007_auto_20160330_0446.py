# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('charge', '0006_auto_20150819_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionalcharge',
            name='categories',
            field=models.ManyToManyField(to='category.Category', blank=True),
        ),
    ]
