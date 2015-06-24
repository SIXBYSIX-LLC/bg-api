# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0005_auto_20150622_1837'),
        ('usr', '0002_auto_20150618_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='favorite_products',
            field=models.ManyToManyField(to='catalog.Product'),
        ),
    ]
