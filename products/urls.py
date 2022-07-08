from django.urls import path

from products.views import ProductListView, ProductView,ReviewView

urlpatterns = [
    path('', ProductListView.as_view()),
    path('/<int:product_id>', ProductView.as_view()),
    path('/<int:product_id>/review', ReviewView.as_view())
]
