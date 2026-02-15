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
    path('',crochetViews.home, name='home'),
    path('owner/',crochetViews.owner,name='owner'),
    path('employee/',crochetViews.employee),
    path('toggle-product/<int:product_id>/', crochetViews.toggle_product_status, name='toggle_product_status'),
    path('product/<int:product_id>/', crochetViews.product_detail, name='product_detail'),
    path('cart/', crochetViews.view_cart, name='view_cart'),
    path('cart/add/', crochetViews.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', crochetViews.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', crochetViews.remove_from_cart, name='remove_from_cart'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)