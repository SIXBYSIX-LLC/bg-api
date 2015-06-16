# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usr', '0005_auto_20150611_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(related_name='owner',
                                    on_delete=django.db.models.deletion.SET_DEFAULT, default=None,
                                    blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
