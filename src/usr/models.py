import uuid

from django.db import models
from miniauth.models import User, UserManager
from django.utils.translation import ugettext as _


class ProfileManager(UserManager):
    pass


class Profile(User):
    """
    Extends auth user to hold User's profile information
    """

    #: User's full name
    fullname = models.CharField(_("Person's full name"), max_length=50)
    #: User's zip code
    zip_code = models.CharField(_('Zip code'), max_length=10)
    #: User's phone number
    phone = models.CharField(_('Phone number'), max_length=20)
    #: Store name that is being displayed while browsing the product and other places
    store_name = models.CharField(_('Store name'), max_length=20, null=True, blank=True,
                                  unique=True)
    #: UUID field to hold verification key for email
    unverified_email_key = models.UUIDField(blank=True, default=uuid.uuid4, editable=False)
    #: Shows if email is verified
    is_email_verified = models.BooleanField(default=False, blank=True)
    #: User's time zone. It can be used for converting datetime instance to user's time zone
    # while displaying the data
    timezone = models.CharField(max_length=30, blank=True, default='UTC')

    objects = ProfileManager()


