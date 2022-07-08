from django.urls import path

from orders.views import ReservationView

urlpatterns = [
    path('/<int:room_id>', ReservationView.as_view())
]