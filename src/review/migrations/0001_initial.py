# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import common.fields


class Migration(migrations.Migration):
    dependencies = [
        ('order', '0008_status_user'),
        ('catalog', '0009_auto_20150819_1259'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('reviewer', models.CharField(max_length=30, editable=False,
                                              choices=[(b'buyer', b'Buyer'),
                                                       (b'seller', b'Seller')])),
                ('comment', models.CharField(default=b'', max_length=1000)),
                ('rating', common.fields.SmallIntegerField()),
                ('order_item', models.ForeignKey(to='order.Item')),
                ('product', models.ForeignKey(editable=False, to='catalog.Product')),
                ('to_user',
                 models.ForeignKey(related_name='+', editable=False, to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='+', default=None, editable=False,
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='orderitem',
            unique_together=set([('user', 'order_item')]),
        ),
    ]
