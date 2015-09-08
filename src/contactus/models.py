"""
======
Models
======
"""

from django.db import models

from common.models import BaseModel, DateTimeFieldMixin


class ContactUs(BaseModel, DateTimeFieldMixin):
    """
    Class to store count us details
    """
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    zip_code = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.CharField(max_length=1000)
