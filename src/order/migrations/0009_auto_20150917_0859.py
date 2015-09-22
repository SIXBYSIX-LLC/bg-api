# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
        ('order', '0008_status_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='contact_info',
            field=djangofuture.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_note',
            field=models.TextField(default=b''),
        ),
    ]
