# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='image'
        ),
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ForeignKey(default=None, blank=True, to='static.File', null=True,
                                    on_delete=models.SET_NULL),
        ),
    ]
