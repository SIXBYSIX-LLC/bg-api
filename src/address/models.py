from django.db import models
from django.contrib.gis.db import models as gis_models

from common.models import BaseModel
from . import constants


class Address(BaseModel):
    TYPES = (
        (constants.TYPE_JOB_SITE, 'Job site'),
        (constants.TYPE_BILLING, 'Billing'),
    )
    #: Owner of the object
    user = models.ForeignKey('miniauth.User')
    #: Location name
    name = models.CharField(max_length=30)
    #: Address 1
    address1 = models.CharField(max_length=254)
    #: Address 2
    address2 = models.CharField(max_length=254, blank=True, null=True, default=None)
    city = models.ForeignKey('cities.City')
    state = models.ForeignKey('cities.Region')
    zip_code = models.CharField(max_length=20)
    country = models.ForeignKey('cities.Country')
    #: Coordinates of the location
    coord = gis_models.PointField(null=True, blank=True)
    #: Type of address
    kind = models.CharField(choices=TYPES, max_length=20)

    Const = constants

    def clean(self):
        raise ValueError('here')
