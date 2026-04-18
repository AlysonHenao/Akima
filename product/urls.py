from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_product_catalog, name='home'),
    path('product/<int:product_id>/', views.show_product_details, name='product_detail'),
    path('administrator/', views.administrator, name='administrator'),
    path('administrator/products/', views.create_product, name='new_product'),
    path('administrator/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('administrator/products/toggle/<int:product_id>/', views.toggle_product, name='toggle_product'),
    path('administrator/colors/create/', views.create_general_color, name='create_color'),
]
