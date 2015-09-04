"""
=====
Model
=====
"""
from django.contrib.auth.models import Group as AuthGroup
from django.db import models

from common.models import BaseModel


class Group(AuthGroup):
    """
    Extends standard django group model features.

    Standard django model have ``name`` field as unique but that's not expected in where user can
    create
    his own group that's why I include title field and name is auto generated while creating.
    """
    #: Title instead of name
    title = models.CharField(max_length=80)
    #: Creator of the group
    user = models.ForeignKey('miniauth.User', blank=True, null=True, editable=False)

    class Meta(BaseModel.Meta):
        unique_together = ('title', 'user')
