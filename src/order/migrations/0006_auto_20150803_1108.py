# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import djangofuture.contrib.postgres.fields.jsonb

import common.fields


class Migration(migrations.Migration):
    dependencies = [
        ('order', '0005_auto_20150727_1059'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='total',
            new_name='cost_breakup',
        ),
        migrations.RemoveField(
            model_name='orderline',
            name='total',
        ),
        migrations.AddField(
            model_name='item',
            name='additional_charge',
            field=common.fields.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='shipping_charge',
            field=common.fields.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='additional_charge',
            field=common.fields.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_charge',
            field=common.fields.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='subtotal',
            field=common.fields.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderline',
            name='additional_charge',
            field=common.fields.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='orderline',
            name='cost_breakup',
            field=djangofuture.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
        migrations.AddField(
            model_name='orderline',
            name='shipping_charge',
            field=common.fields.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='orderline',
            name='subtotal',
            field=common.fields.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='item',
            name='subtotal',
            field=common.fields.FloatField(),
        ),
    ]
