from django.urls import path

from users.views import SigninView, UserView, ReviewView

urlpatterns = [
    path('/signin', SigninView.as_view()),
    path('', UserView.as_view()),
    path('/review', ReviewView.as_view())
]