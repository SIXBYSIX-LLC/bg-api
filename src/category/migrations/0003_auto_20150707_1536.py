# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('category', '0002_auto_20150623_1707'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('name', 'parent')]),
        ),
    ]
