# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('charge', '0004_auto_20150727_1226'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='salestax',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='salestax',
            name='country',
        ),
        migrations.RemoveField(
            model_name='salestax',
            name='state',
        ),
        migrations.DeleteModel(
            name='SalesTax',
        ),
    ]
