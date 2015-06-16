# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('usr', '0003_auto_20150610_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='date_password_reset',
            field=models.DateTimeField(null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='date_password_reset_request',
            field=models.DateTimeField(null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_password_reset',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='password_reset_key',
            field=models.UUIDField(default=uuid.uuid4, editable=False, blank=True),
        ),
    ]
