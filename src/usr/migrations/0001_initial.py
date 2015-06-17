# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('cities', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('miniauth', '0001_initial'),
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
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True,
                                      serialize=False, to=settings.AUTH_USER_MODEL)),
                ('fullname', models.CharField(max_length=50, verbose_name="Person's full name")),
                ('zip_code', models.CharField(max_length=10, verbose_name='Zip code')),
                ('phone', models.CharField(max_length=30, verbose_name='Phone number')),
                ('store_name',
                 models.CharField(max_length=50, unique=True, null=True, verbose_name='Store name',
                                  blank=True)),
                ('unverified_email_key',
                 models.UUIDField(default=uuid.uuid4, editable=False, blank=True)),
                ('is_email_verified', models.BooleanField(default=False)),
                ('timezone', models.CharField(default=b'UTC', max_length=30, blank=True)),
                ('password_reset_key',
                 models.UUIDField(default=uuid.uuid4, editable=False, blank=True)),
                (
                'date_password_reset', models.DateTimeField(null=True, editable=False, blank=True)),
                ('date_password_reset_request',
                 models.DateTimeField(null=True, editable=False, blank=True)),
                ('is_password_reset', models.BooleanField(default=True)),
                ('user', models.ForeignKey(related_name='managers',
                                           on_delete=django.db.models.deletion.SET_DEFAULT,
                                           default=None, blank=True, to=settings.AUTH_USER_MODEL,
                                           null=True)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
            bases=('miniauth.user',),
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
