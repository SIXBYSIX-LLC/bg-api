# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('cities', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesTax',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('value', models.DecimalField(max_digits=4, decimal_places=2)),
                ('unit', models.CharField(max_length=30,
                                          choices=[(b'pct', b'Percentage'), (b'flat', b'Flat')])),
                ('country', models.ForeignKey(to='cities.Country')),
                ('state', models.ForeignKey(to='cities.Region', null=True)),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='salestax',
            unique_together=set([('country', 'state')]),
        ),
    ]
