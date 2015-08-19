# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('shipping', '0003_standardmethod_delivery_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardmethod',
            name='zipcode_end',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
        migrations.AlterField(
            model_name='standardmethod',
            name='zipcode_start',
            field=models.PositiveIntegerField(db_index=True),
        ),
    ]
