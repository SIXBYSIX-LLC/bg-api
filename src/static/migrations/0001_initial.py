# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('url', models.URLField()),
                ('upload_resp',
                 djangofuture.contrib.postgres.fields.jsonb.JSONField(null=True, editable=False,
                                                                      blank=True)),
                ('target', models.CharField(max_length=100, choices=[
                    (b'catalog.Product.images', b'Product Image')])),
                ('target_id', models.CharField(max_length=10)),
                ('user', models.ForeignKey(default=None, blank=True, editable=False,
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
    ]
