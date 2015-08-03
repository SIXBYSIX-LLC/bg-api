# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import djangofuture.contrib.postgres.fields.jsonb

import common.fields


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0006_auto_20150803_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('order_note', models.TextField(default=None, null=True)),
                ('po', models.CharField(default=b'', max_length=50)),
                ('is_paid', models.BooleanField(default=False)),
                ('is_for_order', models.BooleanField()),
                ('is_approve', models.BooleanField(default=False)),
                ('order', models.ForeignKey(to='order.Order')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.CreateModel(
            name='InvoiceLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('is_approve', models.BooleanField(default=False)),
                ('remark', models.TextField(default=b'')),
                ('invoice', models.ForeignKey(to='invoice.Invoice')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
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
                ('qty', models.PositiveSmallIntegerField()),
                ('unit_price', common.fields.FloatField()),
                ('subtotal', common.fields.FloatField()),
                ('shipping_charge', common.fields.FloatField()),
                ('additional_charge', common.fields.FloatField()),
                ('overuse_charge', common.fields.FloatField(default=0)),
                ('cost_breakup', djangofuture.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('date_from', models.DateTimeField(default=None, null=True)),
                ('date_to', models.DateTimeField(default=None, null=True)),
                ('invoice', models.ForeignKey(to='invoice.Invoice')),
                ('invoiceline', models.ForeignKey(to='invoice.InvoiceLine')),
                ('order_item', models.ForeignKey(related_name='invoice_item', to='order.Item')),
                ('user', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='invoice',
            unique_together=set([('user', 'is_for_order')]),
        ),
    ]
