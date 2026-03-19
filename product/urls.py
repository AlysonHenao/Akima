from django.urls import path
from . import views

urlpatterns = [
    # Rf-01 / Rf-02: Display and search product catalog
    path('', views.display_product_catalog, name='home'),

    # Rf-04: Show product details
    path('product/<int:product_id>/', views.show_product_details, name='product_detail'),

    # Panel administración
    path('administrator/', views.administrator, name='administrator'),

    # Rf-28: Create product (+ Rf-05 customize embebido)
    path('administrator/products/', views.create_product, name='new_product'),

    # Rf-29: Edit product (todos los campos)
    path('administrator/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),

    # Rf-29 (soporte): Toggle activo/inactivo
    path('administrator/products/toggle/<int:product_id>/', views.toggle_product, name='toggle_product'),

    # Rf-28 (soporte): Create general color
    path('administrator/colors/create/', views.create_general_color, name='create_color'),
]
