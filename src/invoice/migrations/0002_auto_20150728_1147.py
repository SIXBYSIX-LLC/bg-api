# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('transaction', '0001_initial'),
        ('order', '0005_auto_20150727_1059'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='journal',
            field=models.ForeignKey(related_name='invoice_item', to='transaction.Journal'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='order',
            field=models.ForeignKey(to='order.Order'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='to_user',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='invoice',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
