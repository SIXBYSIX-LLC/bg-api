# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import common.validators


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usr', '0012_auto_20150917_0657'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(max_length=70)),
                ('email', models.EmailField(default=b'', max_length=254)),
                ('phone',
                 models.CharField(max_length=20, validators=[common.validators.phone_number])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='contactinformation',
            unique_together=set([('user', 'name', 'phone')]),
        ),
    ]
