from django.db import models

from core.models import TimeStampModel

class User(TimeStampModel):
    name         = models.CharField(max_length = 30)
    email        = models.CharField(max_length = 255, unique = True)
    phone_number = models.CharField(max_length = 20, null = True, unique = True)
    kakao_pk     = models.BigIntegerField(unique = True)
    credit       = models.DecimalField(max_digits = 10, decimal_places = 2, default = 200000.00)

    class Meta():
        db_table = 'users'

    def __str__(self):
        return f'{self.name} ({self.pk})'

class Review(TimeStampModel):
    user      = models.ForeignKey('User', on_delete = models.CASCADE)
    product   = models.ForeignKey('products.Product', on_delete = models.CASCADE)
    content   = models.TextField()
    image_url = models.TextField(null = True)
    rating    = models.IntegerField()
    room      = models.ForeignKey('products.Room', on_delete = models.SET_NULL, null = True)

    class Meta():
        db_table = 'reviews'