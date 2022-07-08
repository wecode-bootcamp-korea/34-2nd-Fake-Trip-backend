from django.urls import path

from products.views import ProductListView, ProductView
urlpatterns = [
    path('', ProductListView.as_view()),
    path('/<int:product_id>', ProductView.as_view())
]
