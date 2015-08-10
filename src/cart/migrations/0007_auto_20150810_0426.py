# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('cart', '0006_auto_20150806_0512'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='purchase_products',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='rental_products',
        ),
    ]
