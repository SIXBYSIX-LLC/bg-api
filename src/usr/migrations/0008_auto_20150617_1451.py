# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('usr', '0007_auto_20150616_0736'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'default_permissions': ('add', 'change', 'delete', 'view')},
        ),
    ]
