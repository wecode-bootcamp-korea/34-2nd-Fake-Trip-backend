from django.db import models

from core.models import TimeStampModel

class Reservation(TimeStampModel):
    room               = models.ForeignKey('products.Room', on_delete = models.PROTECT)
    reservation_status = models.ForeignKey('ReservationStatus', on_delete = models.SET_NULL, null = True)
    user               = models.ForeignKey('users.User', on_delete = models.PROTECT)
    guest_information  = models.JSONField()
    start_date         = models.DateField()
    end_date           = models.DateField()


class ReservationStatus(models.Model):
    status = models.CharField(max_length = 50)

    class Meta():
        db_table = 'reservation_statuses'

    def __str__(self):
        return f'{self.status} ({self.pk})'