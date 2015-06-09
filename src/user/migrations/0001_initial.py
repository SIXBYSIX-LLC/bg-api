# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('miniauth', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True,
                                      serialize=False, to=settings.AUTH_USER_MODEL)),
                ('fullname', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=10)),
                ('phone', models.CharField(max_length=20)),
            ],
            options={
                'abstract': False,
            },
            bases=('miniauth.user',),
        ),
    ]
