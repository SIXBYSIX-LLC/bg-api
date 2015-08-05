# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('config', djangofuture.contrib.postgres.fields.jsonb.JSONField(default={})),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
    ]
