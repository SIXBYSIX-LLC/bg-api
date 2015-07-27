# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import common.fields


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('category', '0003_auto_20150707_1536'),
        ('charge', '0003_auto_20150702_1631'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalCharge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(default=b'Tax', max_length=50)),
                ('value', common.fields.FloatField()),
                ('unit', models.CharField(max_length=30,
                                          choices=[(b'pct', b'Percentage'), (b'flat', b'Flat')])),
                ('item_kind', models.CharField(max_length=30, choices=[(b'purchase', b'Purchase'),
                                                                       (b'rental', b'Rental'),
                                                                       (b'all', b'All')])),
                ('categories', models.ManyToManyField(to='category.Category')),
                ('user', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='additionalcharge',
            unique_together=set([('name', 'user')]),
        ),
    ]
