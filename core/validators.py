import re

from django.core.exceptions import ValidationError

def validate_phone_number( value):
        PHONE_NUMBER_REGEX  = '\d{3}-\d{3,4}-\d{4}'

        if not re.match(PHONE_NUMBER_REGEX ,value):
            raise ValidationError(message = 'Invalid PhoneNumber') 

        return

class Validators:
    def __init__(self, config):
        self.config = config
        self.action = {
            'names'          : self.validate_names,
            'emails'         : self.validate_emails,
            'phone_numbers'  : self.validate_phone_numbers,
            'dates'          : self.validate_dates
        }
        
        for i in config.keys():
            self.action.get(i)()

    def validate_phone_numbers(self):
        PHONE_NUMBER_REGEX  = '\d{3}-\d{3,4}-\d{4}'
        
        for phone_number in self.config.get('phone_numbers'):
            if not re.match(PHONE_NUMBER_REGEX ,phone_number):
                raise ValidationError(message = 'Invalid PhoneNumber') 

        return

    def validate_emails(self):
        EMAIL_REGEX  = '^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        
        for email in self.config.get('emails'):
            if not re.match(EMAIL_REGEX, email):
                raise ValidationError(message = 'Invalid Email')

        return

    def validate_names(self):
        NAME_REGEX  = '^[가-힣a-zA-Z0-9]+$'
        
        for name in self.config.get('names'):
            if not re.match(NAME_REGEX, name):
                raise ValidationError(message = 'Invalid Name')

        return

    def validate_dates(self):
        DATE_REGEX = '^\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$'
        
        for date in self.config.get('dates'):
            if not re.match(DATE_REGEX, date):
                raise ValidationError(message = 'Invalid Date')
