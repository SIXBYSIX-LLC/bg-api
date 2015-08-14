# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
        ('cart', '0007_auto_20150810_0426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseitem',
            name='cost_breakup',
            field=djangofuture.contrib.postgres.fields.jsonb.JSONField(
                default={b'additional_charge': []}, editable=False),
        ),
        migrations.AlterField(
            model_name='rentalitem',
            name='cost_breakup',
            field=djangofuture.contrib.postgres.fields.jsonb.JSONField(
                default={b'additional_charge': []}, editable=False),
        ),
    ]
