# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangofuture.contrib.postgres.fields.jsonb

import common.fields


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('net_term', models.PositiveSmallIntegerField()),
                ('note', models.TextField(default=None, null=True)),
                ('order_note', models.TextField(default=None, null=True)),
                ('po', models.CharField(default=b'', max_length=50)),
                ('discount_value', common.fields.FloatField()),
                ('discount_kind', models.CharField(default=None, max_length=20, null=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('total', djangofuture.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('due_date', models.DateField()),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(max_length=500)),
                ('qty', models.PositiveSmallIntegerField(default=1)),
                ('unit_price', common.fields.FloatField(max_length=99999999)),
                ('invoice', models.ForeignKey(to='invoice.Invoice')),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
    ]
