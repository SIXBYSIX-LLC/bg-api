from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class FloatField(models.FloatField):
    def __init__(self, min_value=None, max_value=None, precision=None, **kwargs):
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


