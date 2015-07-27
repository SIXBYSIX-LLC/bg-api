# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='billing_address',
            field=djangofuture.contrib.postgres.fields.jsonb.JSONField(default=None),
            preserve_default=False,
        ),
    ]
