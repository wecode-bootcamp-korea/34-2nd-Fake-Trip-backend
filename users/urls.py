from django.urls import path

from users.views import SigninView, ReviewView
urlpatterns = [
    path('/signin', SigninView.as_view()),
    path('/review', ReviewView.as_view()),
]