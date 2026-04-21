from django.contrib import admin
from .models import Order, OrderDetail, ShoppingCart, ItemCart, PaymentMethod, PaymentReceipt, FinancialMovement


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'order_date_formatted', 'formatted_total', 'status']
    list_filter = ['status', 'order_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'id']
    readonly_fields = ['order_date', 'subtotal', 'total', 'formatted_total']
    fieldsets = (
        ('Cliente', {'fields': ('user',)}),
        ('Detalles del pedido', {'fields': ('order_date', 'subtotal', 'discount', 'total', 'formatted_total')}),
        ('Estado', {'fields': ('status', 'customer_note')}),
    )
    
    def order_number(self, obj):
        return f"#{obj.id}" if obj and obj.id else "-"
    order_number.short_description = "Número"
    
    def customer_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else "Invitado"
    customer_name.short_description = "Cliente"
    
    def order_date_formatted(self, obj):
        if not obj or not obj.order_date:
            return "-"
        return obj.order_date.strftime("%d/%m/%Y %H:%M")
    order_date_formatted.short_description = "Fecha"
    
    def formatted_total(self, obj):
        if not obj or obj.total is None:
            return "-"
        return f"${obj.total:,.0f}".replace(',', '.')
    formatted_total.short_description = "Total"


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'product_name', 'color_name', 'size', 'quantity', 'formatted_unit_price']
    list_filter = ['size', 'order__status']
    search_fields = ['order__id', 'product__name']
    readonly_fields = ['subtotal']
    
    def order_id(self, obj):
        return f"#{obj.order.id}"
    order_id.short_description = "Orden"
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = "Producto"
    
    def color_name(self, obj):
        return obj.color_product.general_color.name
    color_name.short_description = "Color"
    
    def formatted_unit_price(self, obj):
        if obj.unit_price is None:
            return "-"
        return f"${obj.unit_price:,.0f}".replace(',', '.')
    formatted_unit_price.short_description = "Precio unitario"


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_display', 'item_count', 'created_date']
    list_filter = ['created_date']
    search_fields = ['user__first_name', 'user__last_name', 'session_key']
    readonly_fields = ['created_date', 'updated_date']
    
    def user_display(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else f"Anónimo ({obj.session_key[:8]})"
    user_display.short_description = "Usuario"
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Items"


admin.site.register(ItemCart)
admin.site.register(PaymentMethod)
admin.site.register(PaymentReceipt)
admin.site.register(FinancialMovement)