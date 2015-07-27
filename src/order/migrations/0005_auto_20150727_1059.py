# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('order', '0004_auto_20150727_0732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='status',
            field=models.CharField(max_length=30, choices=[(b'approved', b'approved'),
                                                           (b'cancelled', b'cancelled'),
                                                           (b'confirmed', b'confirmed'),
                                                           (b'delivered', b'delivered'),
                                                           (b'dispatched', b'dispatched'),
                                                           (b'end_contract', b'end_contract'),
                                                           (b'not_confirmed', b'not_confirmed'),
                                                           (b'picked_up', b'picked_up'),
                                                           (b'ready_to_pickup', b'ready_to_pickup'),
                                                           (b'ready_to_ship', b'ready_to_ship')]),
        ),
    ]
