from django.core.exceptions import ValidationError


def phone_number(value):
    try:
        value = str(value)
    except ValueError:
        raise ValidationError('%s is not a valid phone format' % value)

    if len(value) > 20 or len(value) < 10:
        raise ValidationError('%s is not a valid phone format' % value)

    if value.startswith('+') is False:
        raise ValidationError("Phone number should start with '+'")

    if value.startswith('+0') is True:
        raise ValidationError("Phone number should not contain '0' immediate after '+'")

    if value[1:].isdigit() is False:
        raise ValidationError("Phone number can contain only digit prefix with '+'")
