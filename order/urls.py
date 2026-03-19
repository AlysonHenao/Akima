from django.urls import path
from . import views

urlpatterns = [
    # Rf-06: Add product to cart
    path('cart/add/<int:product_id>/', views.add_product_to_cart, name='add_to_cart'),

    # Rf-06 (soporte): cart management
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/empty/', views.empty_cart, name='empty_cart'),

    # Rf-08 (GET) + Rf-07 + Rf-09 + Rf-26 (POST): página de pago
    path('payment/', views.payment_page, name='payment'),

    # Rf-30: View order information
    path('administrator/orders/', views.view_order_information, name='orders'),

    # Rf-27: Confirm payment
    path('administrator/orders/confirm/<int:receipt_id>/', views.confirm_payment, name='confirm_payment'),

    # Rf-36: Modify order status
    path('administrator/orders/update-status/<int:order_id>/', views.modify_order_status, name='update_order_status'),

    # Rf-11: Check order status
    path('my-orders/', views.check_order_status, name='customer_orders_panel'),
]
