"""
URL configuration for Akima project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from crochet import views as crochetViews

from django.conf.urls.static import static
from django.conf import settings




urlpatterns = [
    path('admin/', admin.site.urls),
    path('payment/', crochetViews.payment, name='payment'),
    path('',crochetViews.home),
    path('administrator/', crochetViews.administrator, name='administrator'),
    path('new_product/',crochetViews.new_product,name='new_product'),
    path('employee/', crochetViews.employee),
    path('product/toggle/<int:product_id>/', crochetViews.toggle_product, name='toggle_product'),
    path('product/<int:product_id>/', crochetViews.product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', crochetViews.add_to_cart, name='add_to_cart'),
    path('cart/', crochetViews.view_cart, name='view_cart'),
    path('update_cart_item/<int:item_id>/', crochetViews.update_cart_item, name='update_cart_item'),
    path('remove_cart_item/<int:item_id>/', crochetViews.remove_cart_item, name='remove_cart_item'),
    path('empty_cart/', crochetViews.empty_cart, name='empty_cart'),
    path('orders/', crochetViews.orders, name='orders'),
    path('orders/confirm/<int:receipt_id>/', crochetViews.confirm_payment, name='confirm_payment'),
    path('orders/update-status/<int:order_id>/', crochetViews.update_order_status, name='update_order_status'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)