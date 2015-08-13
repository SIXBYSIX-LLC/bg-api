# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('invoice', '0004_auto_20150810_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='is_final_invoice',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='item',
            name='order_item',
            field=models.ForeignKey(related_name='invoiceitem_set', to='order.Item'),
        ),
    ]
