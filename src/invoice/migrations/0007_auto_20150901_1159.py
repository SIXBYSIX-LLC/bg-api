# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('invoice', '0006_auto_20150819_1259'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoice',
            options={'default_permissions': ('add', 'change', 'delete', 'view'), 'permissions': (
            ('action_pay', 'Can pay invoice'), ('action_export', 'Can export invoice'))},
        ),
    ]
