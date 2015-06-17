# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('image', models.URLField(null=True, blank=True)),
                ('hierarchy', django.contrib.postgres.fields.ArrayField(size=None, null=True,
                                                                        base_field=models.IntegerField(),
                                                                        blank=True)),
                ('parent',
                 models.ForeignKey(default=None, blank=True, to='category.Category', null=True)),
            ],
            options={
                'db_table': 'category',
            },
        ),
    ]
