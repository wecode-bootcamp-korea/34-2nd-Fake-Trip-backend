from django.urls import path

from products.views import ProductListView, ProductView, ReviewsView, RoomsView

urlpatterns = [
    path('', ProductListView.as_view()),
    path('/<int:product_id>', ProductView.as_view()),
    path('/<int:product_id>/reviews', ReviewsView.as_view()),
    path('/<int:product_id>/rooms', RoomsView.as_view()),
]
