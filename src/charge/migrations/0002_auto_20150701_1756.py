# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('charge', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salestax',
            name='name',
            field=models.CharField(default=b'Tax', max_length=50),
        ),
    ]
