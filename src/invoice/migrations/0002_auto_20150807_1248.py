# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoiceline',
            options={'default_permissions': ('add', 'change', 'delete', 'view'),
                     'permissions': (('can_approve_invoiceline', 'Can approve invoiceline'),)},
        ),
    ]
