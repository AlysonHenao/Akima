import json
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import send_mail
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

from .models import (
    Order, OrderDetail, ShoppingCart, ItemCart,
    PaymentMethod, PaymentReceipt,
)
from product.models import Product, ColorProduct


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

        color_product = get_object_or_404(
            ColorProduct, id=color_id, product=product, available=True
        )
        cart = get_or_create_cart(request)
        existing_item = ItemCart.objects.filter(
            cart=cart, product=product, color_product=color_product, size=size
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
            messages.success(request, f'Cantidad de "{product.name}" actualizada en el carrito.')
        else:
            ItemCart.objects.create(
                cart=cart,
                product=product,
                color_product=color_product,
                size=size,
                quantity=quantity,
                unit_price=product.price
            )
            messages.success(request, f'"{product.name}" agregado al carrito exitosamente.')

        referer = request.META.get('HTTP_REFERER', '/')
        parsed = urlparse(referer)
        return redirect(f"{parsed.path}?carrito=abierto")

    return redirect(request.META.get('HTTP_REFERER', '/'))


def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        item = get_object_or_404(ItemCart, id=item_id, cart=cart)

        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                new_quantity = int(data.get('quantity', 1))
            except (json.JSONDecodeError, ValueError):
                return JsonResponse({'success': False, 'error': 'Datos inválidos.'}, status=400)
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
    item = get_object_or_404(ItemCart, id=item_id, cart=cart)
    product_name = item.product.name
    item.delete()
    messages.success(request, f'"{product_name}" eliminado del carrito.')
    return redirect('view_cart')


def empty_cart(request):
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.success(request, 'Carrito vaciado.')
    return redirect('view_cart')


def payment(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product', 'color_product__general_color')

    if not items.exists():
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('view_cart')

    if request.method == 'POST':
        receipt_file = request.FILES.get('receipt')
        payment_method_id = request.POST.get('payment_method_id')

        if not receipt_file:
            messages.error(request, 'Debes subir un comprobante.')
            return redirect('payment')
        if not payment_method_id:
            messages.error(request, 'Debes seleccionar un método de pago.')
            return redirect('payment')

        payment_method = get_object_or_404(PaymentMethod, id=payment_method_id)
        total = cart.get_total()

        order = Order.objects.create(
            user=cart.user,
            subtotal=total,
            total=total,
            status='Pendiente confirmacion',
        )
        for item in items:
            OrderDetail.objects.create(
                order=order,
                product=item.product,
                color_product=item.color_product,
                size=item.size,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
        PaymentReceipt.objects.create(
            order=order,
            payment_method=payment_method,
            receipt=receipt_file,
            amount=total,
        )
        cart.items.all().delete()
        messages.success(request, '¡Comprobante enviado! Tu pedido será verificado.')
        return redirect('home')

    total = cart.get_total()
    payment_methods = PaymentMethod.objects.filter(active=True)
    return render(request, 'order/payment.html', {
        'items': items,
        'total': total,
        'payment_methods': payment_methods,
    })


def orders(request):
    all_orders = Order.objects.select_related('user').prefetch_related(
        'receipts__payment_method',
        'details__product',
        'details__color_product__general_color'
    ).order_by('-order_date')
    return render(request, 'order/orders.html', {'orders': all_orders})


def confirm_payment(request, receipt_id):
    if request.method == 'POST':
        receipt = get_object_or_404(PaymentReceipt, id=receipt_id)
        receipt.confirm = True
        receipt.confirm_date = timezone.now()
        receipt.save()

        order = receipt.order
        order.status = 'Confirmado'
        order.save()

        if order.user and order.user.email:
            send_mail(
                subject=f'Pedido #{order.id} confirmado - Akima',
                message=(
                    f'Hola {order.user.first_name},\n\n'
                    f'Tu pago ha sido confirmado y tu pedido #{order.id} está en proceso.\n'
                    f'Total: ${order.total}\n\n'
                    f'Gracias por comprar en Akima.'
                ),
                from_email=None,
                recipient_list=[order.user.email],
                fail_silently=True,
            )
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
            messages.error(request, 'Estado no válido.')
    return redirect('orders')