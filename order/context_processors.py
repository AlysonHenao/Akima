from .models import ShoppingCart

def carrito(request):
    if not request.session.session_key:
        return {'carrito_items': [], 'carrito_total': 0}
    cart = ShoppingCart.objects.filter(session_key=request.session.session_key).first()
    if not cart:
        return {'carrito_items': [], 'carrito_total': 0}
    items = cart.items.select_related('product', 'color_product__general_color')
    return {
        'carrito_items': items,
        'carrito_total': cart.get_total()
    }