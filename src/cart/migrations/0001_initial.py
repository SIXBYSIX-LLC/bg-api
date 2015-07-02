# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import djangofuture.contrib.postgres.fields.jsonb

import cart.validators
import common.fields


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0005_auto_20150622_1837'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usr', '0005_auto_20150701_1908'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('date_created_at', models.DateTimeField(auto_now_add=True)),
                ('date_updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('total',
                 djangofuture.contrib.postgres.fields.jsonb.JSONField(default={}, editable=False)),
                ('location', models.ForeignKey(default=None, to='usr.Address', null=True)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
                'db_table': 'cart',
            },
        ),
        migrations.CreateModel(
            name='RentalItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('shipping_kind', models.CharField(max_length=20, choices=[(b'pickup', b'Pickup'), (
                b'delivery', b'Delivery')])),
                ('shipping_cost', common.fields.FloatField(default=0)),
                ('subtotal', common.fields.FloatField(default=0)),
                ('is_shippable', models.BooleanField(default=False)),
                ('qty', models.PositiveSmallIntegerField(default=1)),
                ('date_start',
                 models.DateTimeField(validators=[cart.validators.validate_date_start])),
                ('date_end', models.DateTimeField()),
                ('cost_breakup',
                 djangofuture.contrib.postgres.fields.jsonb.JSONField(default={}, editable=False)),
                ('cart', models.ForeignKey(to='cart.Cart')),
                ('product', models.ForeignKey(to='catalog.Product')),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.AddField(
            model_name='cart',
            name='rental_products',
            field=models.ManyToManyField(to='catalog.Product', through='cart.RentalItem'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(blank=True, editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='rentalitem',
            unique_together=set([('cart', 'product', 'date_start', 'date_end')]),
        ),
    ]
