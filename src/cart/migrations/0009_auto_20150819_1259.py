# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('cart', '0008_auto_20150814_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='is_active',
            field=models.BooleanField(default=True, db_index=True, editable=False),
        ),
    ]
