# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('shipping', '0002_auto_20150702_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='standardmethod',
            name='delivery_days',
            field=models.PositiveSmallIntegerField(default=5),
            preserve_default=False,
        ),
    ]
