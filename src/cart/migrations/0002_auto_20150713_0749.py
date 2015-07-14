# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import common.fields


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0007_auto_20150707_1401'),
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('shipping_kind', models.CharField(max_length=20, choices=[(b'pickup', b'Pickup'), (
                b'delivery', b'Delivery')])),
                ('shipping_cost', common.fields.FloatField(default=0)),
                ('subtotal', common.fields.FloatField(default=0)),
                ('is_shippable', models.BooleanField(default=False)),
                ('qty', models.PositiveSmallIntegerField(default=1)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='rentalitem',
            name='is_postpaid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='cart',
            name='rental_products',
            field=models.ManyToManyField(related_name='+', through='cart.RentalItem',
                                         to='catalog.Product'),
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='cart',
            field=models.ForeignKey(to='cart.Cart'),
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='product',
            field=models.ForeignKey(to='catalog.Product'),
        ),
        migrations.AddField(
            model_name='cart',
            name='purchase_products',
            field=models.ManyToManyField(related_name='+', through='cart.PurchaseItem',
                                         to='catalog.Product'),
        ),
    ]
