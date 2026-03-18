from django.urls import path
from . import views

urlpatterns = [
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/empty/', views.empty_cart, name='empty_cart'),
    path('payment/', views.payment, name='payment'),
    path('administrator/orders/', views.orders, name='orders'),
    path('administrator/orders/confirm/<int:receipt_id>/', views.confirm_payment, name='confirm_payment'),
    path('administrator/orders/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('assigned-products/', views.view_assigned_products, name='assigned_products'),
    path('order-status/', views.view_status_of_orders, name='order_status'),
]