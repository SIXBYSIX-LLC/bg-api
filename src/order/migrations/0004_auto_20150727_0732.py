# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
        ('order', '0003_auto_20150727_0624'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='status',
            name='comment',
        ),
        migrations.AddField(
            model_name='status',
            name='info',
            field=djangofuture.contrib.postgres.fields.jsonb.JSONField(default=None, null=True),
        ),
    ]
