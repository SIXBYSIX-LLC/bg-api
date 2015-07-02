# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

import common.fields


class Migration(migrations.Migration):
    dependencies = [
        ('tax', '0002_auto_20150701_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salestax',
            name='value',
            field=common.fields.FloatField(),
        ),
    ]
