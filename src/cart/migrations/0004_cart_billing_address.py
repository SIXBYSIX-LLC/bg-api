# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('usr', '0007_profile_credit_form'),
        ('cart', '0003_purchaseitem_cost_breakup'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='billing_address',
            field=models.ForeignKey(related_name='+', default=None, to='usr.Address', null=True),
        ),
    ]
