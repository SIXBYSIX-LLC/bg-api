from django.utils import timezone

from common.errors import ValidationError


def validate_date_start(value):
    if (value - timezone.now()).days < 2:
        raise ValidationError('%s must be 2 days ahead of now' % value)
