# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('static', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='target',
            field=models.CharField(max_length=100,
                                   choices=[(b'catalog.Product.images', b'Product Image'),
                                            (b'category.Category.image', b'Category Image')]),
        ),
    ]
