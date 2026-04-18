from django.contrib import admin
from .models import Product, ColorProduct, ProductImage, SetProduct, GeneralColor


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'formatted_price', 'stock', 'active']
    list_filter = ['category', 'active']
    search_fields = ['name', 'description']


@admin.register(ColorProduct)
class ColorProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'general_color', 'available']
    list_filter = ['available', 'general_color']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'url_image']
    search_fields = ['product__name']


admin.site.register(SetProduct)
admin.site.register(GeneralColor)