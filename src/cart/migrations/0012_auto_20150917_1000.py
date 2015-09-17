# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('cart', '0011_auto_20150917_0838'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseitem',
            name='note',
            field=models.CharField(default=b'', max_length=500),
        ),
        migrations.AddField(
            model_name='rentalitem',
            name='note',
            field=models.CharField(default=b'', max_length=500),
        ),
    ]
