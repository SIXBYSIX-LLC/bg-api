# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_default_group(apps, schema_editor):
    # Create default group
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="User")
    Group.objects.get_or_create(name="Device")


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.RunPython(create_default_group)
    ]
