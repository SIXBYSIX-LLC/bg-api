# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('invoice', '0005_auto_20150812_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='is_approve',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='is_for_order',
            field=models.NullBooleanField(default=None, db_index=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='is_paid',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='invoiceline',
            name='is_approve',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='date_from',
            field=models.DateTimeField(default=None, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='date_to',
            field=models.DateTimeField(default=None, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='is_final_invoice',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
