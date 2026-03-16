from django.contrib import admin
from .models import (
    Product, User, GeneralColor, ColorProduct, ProductImage,
    SetProduct, PaymentMethod, Order, OrderDetail, PaymentReceipt,
    Supply, ProductColorSupply, ShoppingCart, ItemCart
)


# Register your models here.

admin.site.register(Product)
admin.site.register(User)
admin.site.register(GeneralColor)
admin.site.register(ColorProduct)
admin.site.register(ProductImage)
admin.site.register(SetProduct)
admin.site.register(PaymentMethod)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(PaymentReceipt)
admin.site.register(Supply)
admin.site.register(ProductColorSupply)
admin.site.register(ShoppingCart)
admin.site.register(ItemCart)