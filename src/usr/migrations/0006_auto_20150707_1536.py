# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('usr', '0005_auto_20150701_1908'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='address',
            unique_together=set([('name', 'user')]),
        ),
    ]
