import uuid
import logging

from django.db import models
from django.utils import timezone
from miniauth.models import User, UserManager
from django.contrib.auth.hashers import make_password, is_password_usable
from django.utils.translation import ugettext as _
from django.core import validators

from common import errors
from . import messages


LOG = logging.getLogger('bgapi.' + __name__)


class ProfileManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """

        now = timezone.now()

        if not email:
            raise ValueError(_('Users must have an email address'))

        preset = dict(email=self.normalize_email(email),
                      is_staff=False,
                      is_active=True,
                      is_superuser=False,
                      last_login=now,
                      date_joined=now)
        user = self.model(**dict(extra_fields.items() + preset.items()))

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create(self, **kwargs):
        """
        Overridden the method to hash password field
        """
        password = kwargs.pop('password', None)
        # is password a raw string?
        if is_password_usable(password) is False:
            kwargs['password'] = make_password(password)

        return super(ProfileManager, self).create(**kwargs)


class Profile(User):
    """
    Extends auth user to hold User's profile information
    """

    #: User's full name
    fullname = models.CharField(_("Person's full name"), max_length=50)
    #: User's zip code
    zip_code = models.CharField(_('Zip code'), max_length=10)
    #: User's phone number
    phone = models.CharField(_('Phone number'), max_length=30)
    #: Store name that is being displayed while browsing the product and other places
    store_name = models.CharField(_('Store name'), max_length=50, null=True, blank=True,
                                  unique=True)
    #: UUID field to hold verification key for email
    unverified_email_key = models.UUIDField(blank=True, default=uuid.uuid4, editable=False)
    #: Shows if email is verified
    is_email_verified = models.BooleanField(default=False, blank=True)
    #: User's time zone. It can be used for converting datetime instance to user's time zone
    # while displaying the data
    timezone = models.CharField(max_length=30, blank=True, default='UTC')

    objects = ProfileManager()

    def change_password(self, old_password, new_password):
        LOG.debug('Changing password', extra={'old_password': old_password,
                                              'new_password': new_password})

        if self.check_password(old_password) is False:
            LOG.warning('Old password does not match', extra={'old_password': old_password})
            raise errors.ValidationError(*messages.ERR_OLD_PWD)
        validators.MinLengthValidator(3).__call__(new_password)

        self.set_password(new_password)

        self.save()
