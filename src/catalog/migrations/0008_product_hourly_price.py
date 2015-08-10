# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

import common.fields


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0007_auto_20150707_1401'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='hourly_price',
            field=common.fields.FloatField(default=0.0),
            preserve_default=False,
        ),
    ]
