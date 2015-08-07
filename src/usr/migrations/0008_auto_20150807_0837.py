# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import common.validators


class Migration(migrations.Migration):
    dependencies = [
        ('usr', '0007_profile_credit_form'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='company_name',
            field=models.CharField(default=b'', max_length=100),
        ),
        migrations.AddField(
            model_name='address',
            name='first_name',
            field=models.CharField(default='', max_length=35),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='last_name',
            field=models.CharField(default='', max_length=35),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='phone',
            field=models.CharField(default='', max_length=20,
                                   validators=[common.validators.phone_number]),
            preserve_default=False,
        ),
    ]
