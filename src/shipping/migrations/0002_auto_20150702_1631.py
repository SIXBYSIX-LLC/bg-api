# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

import common.fields


class Migration(migrations.Migration):
    dependencies = [
        ('shipping', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardmethod',
            name='cost',
            field=common.fields.FloatField(),
        ),
    ]
