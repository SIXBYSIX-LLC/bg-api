"""
======
Models
======
Provides base models for other django.model subclass
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import FieldDoesNotExist

import constants
import validators


class BaseManager(models.Manager):
    pass


class BaseModel(models.Model):
    """
    Adds default permissions and some common methods

    .. note:: Always use this class instead of django.db.models.Model
    """
    objects = BaseManager()

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view')
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        # Add date_updated_at to update_fields if update_fields is specified
        if update_fields is not None and isinstance(update_fields, list):
            try:
                self._meta.get_field('date_updated_at')
                update_fields.append('date_updated_at')
            except FieldDoesNotExist:
                pass

        super(BaseModel, self).save(force_insert=force_insert, force_update=force_update,
                                    using=using, update_fields=update_fields)


class DateTimeFieldMixin(models.Model):
    """
    Abstract class that adds date_created_at, date_updated_at fields to model
    """
    date_created_at = models.DateTimeField(auto_now_add=True)
    date_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AddressBase(BaseModel):
    """
    Abstract class for Address
    """
    TYPES = (
        (constants.Address.TYPE_JOB_SITE, 'Job site'),
        (constants.Address.TYPE_BILLING, 'Billing'),
    )
    #: Owner of the object
    user = models.ForeignKey('miniauth.User', related_name="%(app_label)s_%(class)s_set")
    #: Location name
    name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    company_name = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=20, validators=[validators.phone_number])
    #: Address 1
    address1 = models.CharField(max_length=254)
    #: Address 2
    address2 = models.CharField(max_length=254, blank=True, null=True, default=None)
    city = models.ForeignKey('cities.City', related_name='+')
    state = models.ForeignKey('cities.Region', related_name='+')
    country = models.ForeignKey('cities.Country', related_name='+')
    zip_code = models.CharField(max_length=20)
    #: Coordinates of the location
    coord = gis_models.PointField(null=True, blank=True)
    #: Type of address
    kind = models.CharField(choices=TYPES, max_length=20)

    Const = constants.Address

    class Meta(BaseModel.Meta):
        unique_together = ('name', 'user')
        abstract = True
