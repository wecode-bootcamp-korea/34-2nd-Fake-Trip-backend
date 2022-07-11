from django.urls import path

from users.views import SigninView, UserView
urlpatterns = [
    path('/signin', SigninView.as_view()),
    path('', UserView.as_view())
]