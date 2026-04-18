from django.urls import path
from . import views

urlpatterns = [
    path('cart/add/<int:product_id>/', views.add_product_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/empty/', views.empty_cart, name='empty_cart'),
    path('payment/', views.payment_page, name='payment'),
    path('administrator/orders/', views.view_order_information, name='orders'),
    path('administrator/orders/confirm/<int:receipt_id>/', views.confirm_payment, name='confirm_payment'),
    path('administrator/orders/update-status/<int:order_id>/', views.modify_order_status, name='update_order_status'),
    path('my-orders/', views.check_order_status, name='customer_orders_panel'),
]
