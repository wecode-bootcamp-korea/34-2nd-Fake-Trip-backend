from django.db import models

class Category(models.Model):
    name = models.CharField(max_length = 50)

    class Meta:
        db_table = 'categories'
    
    def __str__(self):
        return f'{self.name} ({self.pk})'

class Product(models.Model):
    name       = models.CharField(max_length = 100)
    grade      = models.IntegerField(null = True)
    check_in   = models.CharField(max_length = 20)
    check_out  = models.CharField(max_length = 20)
    address    = models.CharField(max_length = 255, default = '')
    latitude   = models.DecimalField(max_digits = 13, decimal_places = 10)
    longtitude = models.DecimalField(max_digits = 13, decimal_places = 10)
    region     = models.ForeignKey('Region', on_delete = models.SET_NULL, null = True)
    amenity    = models.ManyToManyField('Amenity', db_table = 'product_amenity')
    user       = models.ManyToManyField(
        'users.User', 
        through = 'users.Review', 
        through_fields = ('product', 'user')
    )
    
    class Meta():
        db_table = 'products'

    def __str__(self):
        return f'{self.name} ({self.pk})'

class Room(models.Model):
    name      = models.CharField(max_length = 100)
    product   = models.ForeignKey('Product', on_delete = models.CASCADE)
    price     = models.DecimalField(max_digits = 15, decimal_places = 10)
    quantity  = models.IntegerField(default = 1)
    size      = models.IntegerField()
    min_guest = models.IntegerField(default = 2)
    max_guest = models.IntegerField(default = 2)

    class Meta():
        db_table = 'rooms'

class Region(models.Model):
    name = models.CharField(max_length = 50)

    class Meta():
        db_table = 'regions'
    
    def __str__(self):
        return f'{self.name} ({self.pk})'

class ProductImage(models.Model):
    url     = models.CharField(max_length = 255)
    product = models.ForeignKey('Product', on_delete = models.CASCADE)
    is_main = models.BooleanField()

    class Meta():
        db_table = 'product_images'

class RoomImage(models.Model):
    url     = models.CharField(max_length = 255)
    product = models.ForeignKey('Product', on_delete = models.CASCADE)
    is_main = models.BooleanField()

    class Meta():
        db_table = 'room_images'

class Amenity(models.Model):
    name = models.CharField(max_length = 30)

    class Meta():
        db_table = 'amenities'

    def __str__(self):
        return f'{self.name} ({self.pk})'