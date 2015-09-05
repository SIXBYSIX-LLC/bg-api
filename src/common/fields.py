"""
======
Fields
======
Extended or custom db fields module.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class FloatField(models.FloatField):
    """
    Float field class with min and max value validation and point precision.
    """

    def __init__(self, min_value=None, max_value=None, precision=None, **kwargs):
        """
        :param float min_value: Minimum value to be accepted
        :param float max_value: Maximum value to be accepted
        :param int precision: Float point precision
        """
        self.min_value, self.max_value, self.precision = min_value, max_value, precision

        self.validators = kwargs.pop('validators', [])
        if self.min_value is not None:
            self.validators.append(MinValueValidator(self.min_value))
        if self.max_value is not None:
            self.validators.append(MaxValueValidator(self.max_value))

        super(FloatField, self).__init__(**kwargs)

    def to_python(self, value):
        value = super(FloatField, self).to_python(value)
        if self.precision is not None and value is not None:
            value = round(value, self.precision)

        return value

    def get_db_prep_save(self, value, connection):
        value = self.to_python(value)
        return super(FloatField, self).get_db_prep_save(value, connection)

    def get_prep_value(self, value):
        value = super(FloatField, self).get_prep_value(value)
        return self.to_python(value)


class SmallIntegerField(models.SmallIntegerField):
    """
    Django's SmallIntegerField with min and max value validation
    """

    def __init__(self, min_value=None, max_value=None, **kwargs):
        """
        :param float min_value: Minimum value to be accepted
        :param float max_value: Maximum value to be accepted
        """
        self.min_value, self.max_value = min_value, max_value

        self.validators = kwargs.pop('validators', [])
        if self.min_value is not None:
            self.validators.append(MinValueValidator(self.min_value))
        if self.max_value is not None:
            self.validators.append(MaxValueValidator(self.max_value))

        super(SmallIntegerField, self).__init__(**kwargs)
