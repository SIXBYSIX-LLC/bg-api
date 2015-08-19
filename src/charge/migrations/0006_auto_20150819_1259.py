# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('charge', '0005_auto_20150818_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionalcharge',
            name='item_kind',
            field=models.CharField(db_index=True, max_length=30,
                                   choices=[(b'purchase', b'Purchase'), (b'rental', b'Rental'),
                                            (b'all', b'All')]),
        ),
    ]
