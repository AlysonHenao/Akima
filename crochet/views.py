from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import (
    Product, ColorProduct, ProductImage, Order,
    GeneralColor, SetProduct, OrderDetail, User,
    ShoppingCart, ItemCart, PaymentMethod, PaymentReceipt,
)
from decimal import Decimal

def home(request):
    products = Product.objects.filter(active=True)
    return render(request, 'home.html', {'products': products})

def payment(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related(
        'id_product',
        'id_product_color__id_general_color'
    )
    if not items.exists():
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('view_cart')

    if request.method == 'POST':
        receipt = request.FILES.get('comprobante') or request.FILES.get('receipt')
        payment_method_id = request.POST.get('metodo_pago_id') or request.POST.get('payment_method_id')

        if not receipt:
            messages.error(request, 'Debes subir un comprobante.')
            return redirect('payment')

        if not payment_method_id:
            messages.error(request, 'Debes seleccionar un método de pago.')
            return redirect('payment')

        payment_method = get_object_or_404(PaymentMethod, id=payment_method_id)
        user = cart.id_user

        total = cart.get_total()
        subtotal = total

        order = Order.objects.create(
            id_user=user,
            subtotal=subtotal,
            total=total,
            status='Pendiente confirmacion',
        )

        for item in items:
            OrderDetail.objects.create(
                id_order=order,
                id_product=item.id_product,
                id_product_color=item.id_product_color,
                size=item.size,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )

        PaymentReceipt.objects.create(
            id_order=order,
            id_payment_method=payment_method,
            receipt=receipt,
            amount=total,
        )

        cart.items.all().delete()
        messages.success(request, 'Comprobante enviado! Tu pedido será verificado.')
        return redirect('/?pedido_confirmado=1')

    total = cart.get_total()
    payment_methods = PaymentMethod.objects.filter(active=True)
    return render(request, "payment.html", {
        "items": items,
        "total": total,
        "payment_methods": payment_methods,
    })

def administrator(request):
    products = Product.objects.all()
    return render(request, 'administrator.html', {'products': products})

def new_product(request):
    if request.method == 'POST':
        try:
            product = Product.objects.create(
                name=request.POST.get('name'),
                category=request.POST.get('category'),
                description=request.POST.get('description'),
                price=Decimal(request.POST.get('price')),
                stock=int(request.POST.get('stock', 0)),
                manufacturing_time=int(request.POST.get('manufacturing_time')),
                active=request.POST.get('active') == 'on',
                manufacturing_guide=request.FILES.get('manufacturing_guide'),
                size_guide=request.FILES.get('size_guide'),
            )
            color_ids = request.POST.getlist('colors')
            for color_id in color_ids:
                ColorProduct.objects.create(
                    id_product=product,
                    id_general_color_id=color_id,
                    available=True
                )
            images = request.FILES.getlist('images')
            for image in images[:5]:
                ProductImage.objects.create(
                    id_product=product,
                    url_image=image
                )
            if product.category == 'Set':
                set_product_ids = request.POST.getlist('set_products')
                for product_id in set_product_ids:
                    quantity = request.POST.get(f'set_quantity_{product_id}')
                    price = request.POST.get(f'set_price_{product_id}')
                    if quantity and price:
                        SetProduct.objects.create(
                            id_set_product=product,
                            id_individual_product_id=product_id,
                            quantity=int(quantity),
                            set_price=Decimal(price)
                        )
            
            messages.success(request, f'¡Producto "{product.name}" creado exitosamente!')

            return redirect('new_product')
        except Exception as e:
            messages.error(request, f'Error al crear producto: {str(e)}')
    
    context = {
        'products': Product.objects.all().prefetch_related(
            'colors__id_general_color',
            'images',
            'set_components__id_individual_product'
        ),
        'colors': GeneralColor.objects.all().order_by('name'),
        'individual_products': Product.objects.exclude(category='Set').filter(active=True)
    }

    return render(request, 'new_product.html', context)

def toggle_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.active = not product.active
    product.save()
    state = "activado" if product.active else "desactivado"
    messages.success(request, f'Producto "{product.name}" {state}.')
    return redirect('new_product')

def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.prefetch_related(
            'colors__id_general_color',
            'images'
        ),
        id=product_id,
        active=True
    )
    available_colors = product.colors.filter(available=True).select_related('id_general_color')
    sizes = [code for code, _ in OrderDetail.SIZE]
    return render(request, 'producto_detalle.html', {
        'product': product,
        'available_colors': available_colors,
        'sizes': sizes,
    })


def employee(request):

    return render(request, 'employee.html')


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, created = ShoppingCart.objects.get_or_create(session_key=session_key)
    return cart


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, active=True)
        color_id = request.POST.get('color')
        size = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))
        product_color = get_object_or_404(
            ColorProduct,
            id=color_id,
            id_product=product,
            available=True
        )
        cart = get_or_create_cart(request)
        existing_item = ItemCart.objects.filter(
            id_cart=cart,
            id_product=product,
            id_product_color=product_color,
            size=size
        ).first()
        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
            messages.success(request, f'Cantidad de "{product.name}" actualizada en el carrito.')
        else:
            ItemCart.objects.create(
                id_cart=cart,
                id_product=product,
                id_product_color=product_color,
                size=size,
                quantity=quantity,
                unit_price=product.price
            )
            messages.success(request, f'"{product.name}" agregado al carrito exitosamente.')
        return redirect('view_cart')
    return redirect('home')


def view_cart(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related(
        'id_product',
        'id_product_color__id_general_color'
    ).prefetch_related('id_product__images')
    total = cart.get_total()
    total_units = sum(item.quantity for item in items)
    context = {
        'cart': cart,
        'items': items,
        'total': total,
        'total_units': total_units,
    }
    return render(request, 'cart.html', context)


def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        item = get_object_or_404(ItemCart, id=item_id, id_cart=cart)
        import json
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                new_quantity = int(data.get('quantity', 1))
            except:
                new_quantity = int(request.POST.get('quantity', 1))
        else:
            new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            item.quantity = new_quantity
            item.save()
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'subtotal': float(item.get_subtotal()),
                    'cart_total': float(cart.get_total())
                })
            messages.success(request, 'Cantidad actualizada en el carrito.')
        else:
            item.delete()
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'deleted': True,
                    'cart_total': float(cart.get_total())
                })
            messages.success(request, 'Producto eliminado del carrito.')
    return redirect('view_cart')


def remove_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(ItemCart, id=item_id, id_cart=cart)
    product_name = item.id_product.name
    item.delete()
    messages.success(request, f'"{product_name}" eliminado del carrito.')
    return redirect('view_cart')


def empty_cart(request):
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.success(request, 'Carrito vaciado.')
    return redirect('view_cart')

def orders(request):
    orders = Order.objects.select_related('id_user').prefetch_related(
        'receipt__id_payment_method',
        'details__id_product',
        'details__id_product_color__id_general_color'
    ).order_by('-order_date')
    return render(request, 'orders.html', {'orders': orders})


def confirm_payment(request, receipt_id):
    if request.method == 'POST':
        receipt = get_object_or_404(PaymentReceipt, id=receipt_id)
        receipt.confirm = True
        receipt.confirm_date = timezone.now()
        receipt.save()
        order = receipt.id_order
        order.status = 'Confirmado'
        order.save()
        messages.success(request, f'Pago del pedido #{order.id} confirmado exitosamente.')
    return redirect('orders')

def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in Order.STATUS]
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f'Estado del Pedido #{order.id} actualizado a "{new_status}".')
        else:
            messages.error(request, 'Estado no válidos.')
    return redirect('orders')