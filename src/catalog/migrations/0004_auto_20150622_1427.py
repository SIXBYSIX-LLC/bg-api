# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0003_auto_20150622_1259'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='inventory',
            unique_together=set([('product', 'serial_no')]),
        ),
    ]
