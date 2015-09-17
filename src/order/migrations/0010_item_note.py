# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('order', '0009_auto_20150917_0859'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='note',
            field=models.CharField(default=b'', max_length=500),
        ),
    ]
