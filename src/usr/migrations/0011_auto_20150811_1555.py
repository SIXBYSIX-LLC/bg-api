# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('usr', '0010_auto_20150810_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.ForeignKey(related_name='+', to='cities.City'),
        ),
        migrations.AlterField(
            model_name='address',
            name='country',
            field=models.ForeignKey(related_name='+', to='cities.Country'),
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.ForeignKey(related_name='+', to='cities.Region'),
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(related_name='usr_address_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
