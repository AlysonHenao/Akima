from django.contrib import admin
from .models import Order, OrderDetail, ShoppingCart, ItemCart, PaymentMethod, PaymentReceipt, FinancialMovement

admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(ShoppingCart)
admin.site.register(ItemCart)
admin.site.register(PaymentMethod)
admin.site.register(PaymentReceipt)
admin.site.register(FinancialMovement)