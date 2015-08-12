# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.gis.db.models.fields

import common.validators


class Migration(migrations.Migration):
    dependencies = [
        ('cities', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0006_auto_20150803_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('first_name', models.CharField(max_length=35)),
                ('last_name', models.CharField(max_length=35)),
                ('company_name', models.CharField(default=b'', max_length=100)),
                ('phone',
                 models.CharField(max_length=20, validators=[common.validators.phone_number])),
                ('address1', models.CharField(max_length=254)),
                ('address2', models.CharField(default=None, max_length=254, null=True, blank=True)),
                ('zip_code', models.CharField(max_length=20)),
                ('coord',
                 django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('kind', models.CharField(max_length=20, choices=[(b'job_site', b'Job site'),
                                                                  (b'billing', b'Billing')])),
                ('city', models.ForeignKey(related_name='+', to='cities.City')),
                ('country', models.ForeignKey(related_name='+', to='cities.Country')),
                ('state', models.ForeignKey(related_name='+', to='cities.Region')),
                ('user',
                 models.ForeignKey(related_name='order_address_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.RemoveField(
            model_name='order',
            name='billing_address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_address',
        ),
        migrations.AddField(
            model_name='order',
            name='billing_address',
            field=models.ForeignKey(related_name='+', to='order.Address'),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(related_name='+', to='order.Address'),
        ),
        migrations.AlterUniqueTogether(
            name='address',
            unique_together=set([('name', 'user')]),
        ),
    ]
