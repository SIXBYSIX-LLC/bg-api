# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):
    dependencies = [
        ('cities', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('address1', models.CharField(max_length=254)),
                ('address2', models.CharField(default=None, max_length=254, null=True, blank=True)),
                ('zip_code', models.CharField(max_length=20)),
                ('coord',
                 django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('kind', models.CharField(max_length=20, choices=[(b'job_site', b'Job site'),
                                                                  (b'billing', b'Billing')])),
                ('city', models.ForeignKey(to='cities.City')),
                ('country', models.ForeignKey(to='cities.Country')),
                ('state', models.ForeignKey(to='cities.Region')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
    ]
