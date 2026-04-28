from .models import ShoppingCart

def carrito(request):
    empty_cart_context = {
        'carrito_items': [],
        'carrito_total': '$0',
    }

    if not request.session.session_key:
        return empty_cart_context

    cart = ShoppingCart.objects.filter(
        session_key=request.session.session_key
    ).first()

    if not cart:
        return empty_cart_context

    items = cart.items.select_related(
        'product',
        'color_product__general_color'
    )

    return {
        'carrito_items': items,
        'carrito_total': cart.formatted_total,
    }