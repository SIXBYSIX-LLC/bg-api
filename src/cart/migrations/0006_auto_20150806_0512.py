# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
        ('cart', '0005_auto_20150803_0859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseitem',
            name='cost_breakup',
            field=djangofuture.contrib.postgres.fields.jsonb.JSONField(
                default={b'additional_charge': {}}, editable=False),
        ),
        migrations.AlterField(
            model_name='rentalitem',
            name='cost_breakup',
            field=djangofuture.contrib.postgres.fields.jsonb.JSONField(
                default={b'additional_charge': {}}, editable=False),
        ),
        migrations.AlterField(
            model_name='rentalitem',
            name='is_postpaid',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='purchaseitem',
            unique_together=set([('cart', 'product')]),
        ),
    ]
