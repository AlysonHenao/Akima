from django.contrib import admin
from .models import Product, ColorProduct, ProductImage, SetProduct, GeneralColor

admin.site.register(Product)
admin.site.register(ColorProduct)
admin.site.register(ProductImage)
admin.site.register(SetProduct)
admin.site.register(GeneralColor)