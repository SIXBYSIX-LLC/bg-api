# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('usr', '0004_auto_20150611_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='is_password_reset',
            field=models.BooleanField(default=True),
        ),
    ]
