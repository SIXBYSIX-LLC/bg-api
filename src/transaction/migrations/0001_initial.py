# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import djangofuture.contrib.postgres.fields.jsonb

import common.fields


class Migration(migrations.Migration):
    dependencies = [
        ('invoice', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('expected_amt', common.fields.FloatField()),
                ('received_amt', common.fields.FloatField()),
                ('using', models.CharField(max_length=30)),
                ('status', models.CharField(max_length=30)),
                ('response', djangofuture.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('invoice', models.ForeignKey(to='invoice.Invoice')),
                ('payer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
    ]
