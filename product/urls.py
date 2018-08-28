from django.urls import path
from . import views
urlpatterns = [
    path('', views.get_product_list, name='product_list'),
    path('category/<int:category_id>', views.get_products_by_category, name='category'),
    path('<str:website_id>/<str:original_id>', views.get_product_by_id, name='product_detail'),
    path('classify', views.classify, name='classify'),
    path('<str:original_id>', views.get_product_comment_id, name='product_comment'),
]