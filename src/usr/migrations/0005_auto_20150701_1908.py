# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
        ('usr', '0004_profile_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='settings',
            field=djangofuture.contrib.postgres.fields.jsonb.JSONField(
                default={b'daily_price_till_days': 3, b'minimum_contract_period': 5,
                         b'weekly_price_till_days': 25}),
        ),
    ]
