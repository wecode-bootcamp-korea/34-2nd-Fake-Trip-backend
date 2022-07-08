import re

from django.core.exceptions import ValidationError

def validate_phone_number(value):
    PHONE_NUMBER_REGEX  = '\d{3}-\d{3,4}-\d{4}'

    if not re.match(PHONE_NUMBER_REGEX ,value):
        raise ValidationError(message = 'Invalid PhoneNumber')