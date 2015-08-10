# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('invoice', '0002_auto_20150807_1248'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoice',
            options={'default_permissions': ('add', 'change', 'delete', 'view'),
                     'permissions': (('can_pay_invoice', 'Can pay invoice'),)},
        ),
    ]
