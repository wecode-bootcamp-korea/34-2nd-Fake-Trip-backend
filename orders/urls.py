from django.urls import path

from orders.views import ReservationView

urlpatterns = [
    path('/reservation', ReservationView.as_view())
] 