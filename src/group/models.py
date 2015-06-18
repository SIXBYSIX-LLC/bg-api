from django.contrib.auth.models import Group as AuthGroup
from django.db import models

from common.models import BaseModel


class Group(AuthGroup):
    title = models.CharField(max_length=80)
    user = models.ForeignKey('miniauth.User', blank=True, null=True)

    class Meta(BaseModel.Meta):
        unique_together = ('title', 'user')
