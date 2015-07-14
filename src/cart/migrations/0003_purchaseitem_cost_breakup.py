# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
        ('cart', '0002_auto_20150713_0749'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseitem',
            name='cost_breakup',
            field=djangofuture.contrib.postgres.fields.jsonb.JSONField(default={}, editable=False),
        ),
    ]
