# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangofuture.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    dependencies = [
        ('cart', '0010_auto_20150917_0657'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='contact_info',
            field=djangofuture.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
        migrations.AddField(
            model_name='cart',
            name='delivery_note',
            field=models.TextField(default=b''),
        ),
    ]
