from django.contrib import admin
from .models import Product, Cart, CartItem

admin.site.register(Product)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

class CartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'created_at', 'get_item_count', 'get_total']
    inlines = [CartItemInline]

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)