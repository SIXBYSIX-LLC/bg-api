# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('cart', '0009_auto_20150819_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rentalitem',
            name='date_start',
            field=models.DateTimeField(),
        ),
    ]
