# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

import common.fields


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0005_auto_20150622_1837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='daily_price',
            field=common.fields.FloatField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='monthly_price',
            field=common.fields.FloatField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='sell_price',
            field=common.fields.FloatField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='weekly_price',
            field=common.fields.FloatField(),
        ),
    ]
