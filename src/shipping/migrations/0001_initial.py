# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('cities', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usr', '0003_profile_favorite_products'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('zipcode_start', models.PositiveIntegerField()),
                ('zipcode_end', models.PositiveIntegerField(default=0)),
                ('cost', models.DecimalField(max_digits=10, decimal_places=2)),
                ('country', models.ForeignKey(to='cities.Country')),
                ('origin', models.ForeignKey(to='usr.Address')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
    ]
