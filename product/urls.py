from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('administrator/', views.administrator, name='administrator'),
    path('administrator/products/', views.new_product, name='new_product'),
    path('administrator/products/toggle/<int:product_id>/', views.toggle_product, name='toggle_product'),
    path('administrator/colors/create/', views.create_color, name='create_color'),
]