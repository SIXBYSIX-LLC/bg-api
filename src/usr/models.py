"""
======
Models
======
"""

import uuid
import logging

from django.db import models
from django.utils import timezone
from miniauth.models import User, UserManager
from django.contrib.auth.hashers import make_password, is_password_usable
from django.utils.translation import ugettext as _
from django.core import validators
from djangofuture.contrib.postgres import fields as pg_fields

from common import errors, validators as ex_validators
from common.models import BaseModel, AddressBase
from . import messages, signals


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
                      date_joined=now,
                      password=password)
        user = self.create(**dict(extra_fields.items() + preset.items()))

        return user

    def create(self, **kwargs):
        """
        Overridden the method to hash password field
        """
        password = kwargs.pop('password', None)
        # is password a raw string?
        if is_password_usable(password) is False:
            kwargs['password'] = make_password(password)

        user = super(ProfileManager, self).create(**kwargs)

        signals.user_registered.send(instance=user)

        return user

    def generate_password_reset_key(self, email):
        try:
            user = self.get(email=email)
        except Profile.DoesNotExist:
            raise errors.ValidationError(*messages.ERR_EMAIL_NOT_EXISTS)

        if user.is_password_reset is False:
            signals.reset_password_request.send(instance=user, retry=True)
            return

        user.is_password_reset = False
        user.date_password_reset_request = timezone.now()
        user.password_reset_key = uuid.uuid4()
        user.save(update_fields=['is_password_reset', 'date_password_reset_request',
                                 'password_reset_key'])

        signals.reset_password_request.send(instance=user, retry=False)

    def reset_password(self, email, reset_key, new_password):
        try:
            user = self.get(email=email)
        except Profile.DoesNotExist:
            raise errors.ValidationError(*messages.ERR_EMAIL_NOT_EXISTS)

        if str(user.password_reset_key) != reset_key:
            raise errors.ValidationError(*messages.ERR_EMAIL_PW_KEY_MISMATCH)
        if user.is_password_reset is True:
            raise errors.ValidationError(*messages.ERR_PW_RESET_KEY_USED)

        user.set_password(new_password)
        # changing the key so user cannot use same key again
        user.password_reset_key = uuid.uuid4()
        user.date_password_reset = timezone.now()
        user.is_password_reset = True

        user.save(update_fields=['password', 'password_reset_key', 'date_password_reset',
                                 'is_password_reset'])

        signals.reset_password_request.send(instance=user)

    def verify_email(self, email_key):
        """
        Verify email address using email_key
        """
        try:
            user = self.get(unverified_email_key=email_key)
        except (Profile.DoesNotExist, ValueError):
            raise errors.ValidationError(*messages.ERR_INVALID_EMAIL_KEY)

        user.unverified_email_key = uuid.uuid4()
        user.is_email_verified = True

        user.save(update_fields=['is_email_verified', 'unverified_email_key'])

        signals.user_verified_email.send(instance=user)

    def resend_email_verification(self, email):
        """
        Re-sends email verification mail by email
        """
        try:
            user = self.get(email=email)
        except Profile.DoesNotExist:
            raise errors.NotFound(*messages.ERR_EMAIL_NOT_EXISTS)

        user.send_email_verification()


class Profile(User):
    """
    Class that extends user auth to store User's profile information
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
    #: Unique that is used to reset password
    password_reset_key = models.UUIDField(blank=True, default=uuid.uuid4, editable=False)
    #: Date time that holds the last time stamp of password reset done successfully
    date_password_reset = models.DateTimeField(blank=True, null=True, editable=False)
    #: Date time that holds the time stamp of last password reset request
    date_password_reset_request = models.DateTimeField(blank=True, null=True, editable=False)
    #: Stores boolean if the password is reset using the key. The idea of keeping this variable
    #: is to check if the new password reset key should be generated each time user requests or it
    #: should be generated only if old key is not used. I thought it this way because sometimes
    #: email gets delayed and user try and try again and all email contains different key that
    #: makes user confused which key should be used to reset password
    is_password_reset = models.BooleanField(blank=True, default=True)
    #: The user under which the actual user is
    user = models.ForeignKey(User, blank=True, null=True, default=None,
                             on_delete=models.SET_DEFAULT, related_name='members')
    settings = pg_fields.JSONField(default={
        'hourly_price_till_hours': 4,
        'daily_price_till_days': 3,
        'weekly_price_till_days': 14,
        'minimum_contract_period': 0,
        'minimum_rent_notice_period': 0,
    })
    #: User's credit form, usually a PDF that contains account other personal information about
    # user. It helps to seller to authentic the user
    credit_form = models.ForeignKey('static.File', null=True, default=None)
    #: Favorited products
    favorite_products = models.ManyToManyField('catalog.Product')

    objects = ProfileManager()

    class Meta(User.Meta, BaseModel.Meta):
        pass

    @property
    def parent(self):
        return self.user

    @property
    def pytz(self):
        """
        :return: pytz object of user's timezone
        """
        return timezone.pytz.timezone(self.timezone)

    def localtime(self, dt):
        """
        Convert datetime object to user's time zone

        :param DateTime dt: Date time object to be converted
        :return: Converted date time object
        """
        return timezone.localtime(dt, self.pytz)

    def change_password(self, old_password, new_password):
        """
        Helper method to user change password

        :param str old_password: Old password
        :param str new_password: New password
        :send signal: password_changed
        """
        LOG.debug('Changing password', extra={'old_password': old_password,
                                              'new_password': new_password})

        if self.check_password(old_password) is False:
            LOG.warning('Old password does not match', extra={'old_password': old_password})
            raise errors.ValidationError(*messages.ERR_OLD_PWD)
        validators.MinLengthValidator(3).__call__(new_password)

        self.set_password(new_password)
        self.save()

        signals.password_changed.send(instance=self)


class Address(AddressBase):
    """
    Class to store address book for user
    """
    pass


class ContactInformation(BaseModel):
    """
    Class to store contact information user has filled while checking out
    """
    user = models.ForeignKey('miniauth.User')
    name = models.CharField(max_length=70)
    email = models.EmailField(default='')
    phone = models.CharField(max_length=20, validators=[ex_validators.phone_number])

    class Meta(BaseModel.Meta):
        unique_together = ('user', 'name', 'phone')
