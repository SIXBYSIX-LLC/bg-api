from django.db import models
from miniauth.models import User, UserManager


class ProfileManager(UserManager):
    pass


class Profile(User):
    fullname = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)

    objects = ProfileManager()
