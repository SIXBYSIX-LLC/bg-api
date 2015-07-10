# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
        ('cities', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cart', '0001_initial'),
        ('catalog', '0007_auto_20150707_1401'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('address', models.TextField()),
                ('zip_code', models.CharField(max_length=15)),
                ('total', djangofuture.contrib.postgres.fields.jsonb.JSONField()),
                ('cart', models.ForeignKey(to='cart.Cart')),
                ('city', models.ForeignKey(to='cities.City')),
                ('country', models.ForeignKey(to='cities.Country')),
                ('state', models.ForeignKey(to='cities.Region')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
                'db_table': 'order',
            },
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('total',
                 djangofuture.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('order', models.ForeignKey(to='order.Order')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RentalItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('detail', djangofuture.contrib.postgres.fields.jsonb.JSONField()),
                ('subtotal', models.FloatField()),
                ('cost_breakup', djangofuture.contrib.postgres.fields.jsonb.JSONField()),
                ('qty', models.PositiveSmallIntegerField()),
                ('shipping_kind', models.CharField(max_length=20)),
                ('shipping_method', models.CharField(max_length=30, null=True)),
                ('payment_method', models.CharField(default=b'postpaid', max_length=20)),
                ('date_start', models.DateTimeField()),
                ('date_end', models.DateTimeField()),
                ('inventory', models.ForeignKey(default=None, to='catalog.Inventory', null=True)),
                ('order', models.ForeignKey(to='order.Order')),
                ('orderline', models.ForeignKey(to='order.OrderLine')),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(max_length=30, choices=[(b'approved', b'approved'),
                                                                    (b'cancelled', b'cancelled'),
                                                                    (b'confirmed', b'confirmed'),
                                                                    (b'delivered', b'delivered'),
                                                                    (b'dispatched', b'dispatched'),
                                                                    (b'not_confirmed',
                                                                     b'not_confirmed'),
                                                                    (b'picked_up', b'picked_up'), (
                    b'ready_to_pickup', b'ready_to_pickup'), (b'ready_to_ship',
                                                              b'ready_to_ship')])),
                ('comment', models.TextField(default=None, null=True)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='rentalitem',
            name='statuses',
            field=models.ManyToManyField(to='order.Status'),
        ),
        migrations.AddField(
            model_name='rentalitem',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
