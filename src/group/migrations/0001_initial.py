# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0007_auto_20150617_1815'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('group_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True,
                                      serialize=False, to='auth.Group')),
                ('title', models.CharField(max_length=80)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
            bases=('auth.group',),
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=set([('title', 'user')]),
        ),
    ]
