# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import common.fields


class Migration(migrations.Migration):
    dependencies = [
        ('cart', '0004_cart_billing_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='total',
            new_name='cost_breakup',
        ),
        migrations.RenameField(
            model_name='purchaseitem',
            old_name='shipping_cost',
            new_name='additional_charge',
        ),
        migrations.RenameField(
            model_name='rentalitem',
            old_name='shipping_cost',
            new_name='additional_charge',
        ),
        migrations.AddField(
            model_name='cart',
            name='additional_charge',
            field=models.FloatField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='cart',
            name='shipping_charge',
            field=models.FloatField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='cart',
            name='subtotal',
            field=models.FloatField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='shipping_charge',
            field=common.fields.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='rentalitem',
            name='shipping_charge',
            field=common.fields.FloatField(default=0),
        ),
    ]
