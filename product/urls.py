from django.urls import path
from . import views
urlpatterns = [
    path('', views.get_product_list, name='product_list'),
    path('<str:original_id>', views.get_product_by_id, name='product_detail'),
]