# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
from django.conf import settings
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
        ('usr', '0002_auto_20150618_1512'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('serial_no', models.CharField(max_length=50, null=True, blank=True)),
                ('source', models.CharField(default=b'purchased', max_length=50, blank=True,
                                            choices=[(b'purchased', b'Purchased'),
                                                     (b'rented', b'Rented from others')])),
                ('is_active', models.BooleanField()),
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('images', django.contrib.postgres.fields.ArrayField(size=10, null=True,
                                                                     base_field=models.URLField(),
                                                                     blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('brand', models.CharField(max_length=100)),
                ('daily_price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('weekly_price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('monthly_price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('sell_price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('is_active', models.BooleanField(default=False)),
                ('sku', models.CharField(max_length=30, blank=True)),
                ('attributes',
                 djangofuture.contrib.postgres.fields.jsonb.JSONField(null=True, blank=True)),
                ('tags', django.contrib.postgres.fields.ArrayField(size=None, null=True,
                                                                   base_field=models.CharField(
                                                                       max_length=30), blank=True)),
                ('condition',
                 models.CharField(max_length=50, choices=[(b'new', b'New'), (b'used', b'Used')])),
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(to='category.Category')),
                ('location', models.ForeignKey(to='usr.Address')),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.AddField(
            model_name='inventory',
            name='product',
            field=models.ForeignKey(to='catalog.Product'),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together=set([('user', 'sku')]),
        ),
    ]
