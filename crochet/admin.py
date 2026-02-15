from django.contrib import admin
from .models import (
    Producto, Usuario, ColorGeneral, ProductoColor, ProductoImagen, 
    SetProducto, MetodoPago, Pedido, PedidoDetalle, ComprobantePago, 
    Insumo, ProductoColorInsumo, CarritoCompra, CarritoItem
)


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
admin.site.register(Insumo)
admin.site.register(ProductoColorInsumo)
admin.site.register(CarritoCompra)
admin.site.register(CarritoItem)