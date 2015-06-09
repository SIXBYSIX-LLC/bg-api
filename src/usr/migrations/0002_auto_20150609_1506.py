# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('usr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='store_name',
            field=models.CharField(max_length=20, unique=True, null=True, verbose_name='Store name',
                                   blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='timezone',
            field=models.CharField(default=b'UTC', max_length=30, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='unverified_email_key',
            field=models.UUIDField(default=uuid.uuid4, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='fullname',
            field=models.CharField(max_length=50, verbose_name="Person's full name"),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(max_length=20, verbose_name='Phone number'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='zip_code',
            field=models.CharField(max_length=10, verbose_name='Zip code'),
        ),
    ]
