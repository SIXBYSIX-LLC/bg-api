# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('invoice', '0003_auto_20150810_1519'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoice',
            options={'default_permissions': ('add', 'change', 'delete', 'view'),
                     'permissions': (('action_pay', 'Can pay invoice'),)},
        ),
        migrations.AlterModelOptions(
            name='invoiceline',
            options={'default_permissions': ('add', 'change', 'delete', 'view'),
                     'permissions': (('action_approve', 'Can approve invoiceline'),)},
        ),
    ]
