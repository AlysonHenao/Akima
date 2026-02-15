from django.contrib import admin
from .models import Producto, Usuario, ColorGeneral, ProductoColor, ProductoImagen, SetProducto, MetodoPago, Pedido, PedidoDetalle, ComprobantePago


# Register your models here.

admin.site.register(Producto)
admin.site.register(Usuario)
admin.site.register(ColorGeneral)
admin.site.register(ProductoColor)
admin.site.register(ProductoImagen)
admin.site.register(SetProducto)
admin.site.register(MetodoPago)
admin.site.register(Pedido)
admin.site.register(PedidoDetalle)
admin.site.register(ComprobantePago)