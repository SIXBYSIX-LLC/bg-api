# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import catalog.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0002_auto_20150619_2023'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='user',
            field=models.ForeignKey(default=None, blank=True, editable=False,
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(to='category.Category',
                                    validators=[catalog.models.validate_category_is_leaf]),
        ),
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(default=None, max_length=30, blank=True),
        ),
    ]
