from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Order, OrderDetail, ShoppingCart, ItemCart,
    PaymentMethod, PaymentReceipt, User
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
        path = referer.split('?')[0]
        return redirect(path + '?carrito=abierto')

    return redirect(request.META.get('HTTP_REFERER', '/'))


def update_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(ItemCart, id=item_id, cart=cart)
    nueva_cantidad = int(request.GET.get('cantidad', 1))
    next_url = request.GET.get('next', '/')

    if nueva_cantidad > 0:
        item.quantity = nueva_cantidad
        item.save()
    else:
        item.delete()

    return redirect(next_url + '?carrito=abierto')


def remove_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(ItemCart, id=item_id, cart=cart)
    item.delete()
    referer = request.META.get('HTTP_REFERER', '/').split('?')[0]
    return redirect(referer + '?carrito=abierto')


def empty_cart(request):
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.success(request, 'Carrito vaciado.')
    return redirect('/?carrito=abierto')


def payment(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product', 'color_product__general_color')

    if not items.exists():
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('/?carrito=abierto')

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

        cliente_nombre = f"{order.user.first_name} {order.user.last_name}" if order.user else "Cliente invitado"

        send_mail(
            subject=f'Nuevo comprobante de pago - Pedido #{order.id}',
            message=(
                f'El cliente {cliente_nombre} '
                f'ha subido un comprobante de pago.\n\n'
                f'Pedido: #{order.id}\n'
                f'Total: ${order.total}\n'
                f'Método de pago: {payment_method.name}\n\n'
                f'Ingresa al panel de administración para confirmarlo.'
            ),
            from_email=None,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
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


def customer_orders_panel(request):
    customers = User.objects.filter(role='cliente').order_by('first_name', 'last_name')
    selected_customer_id = request.GET.get('user_id')
    selected_customer = None
    orders = Order.objects.none()

    if selected_customer_id:
        selected_customer = get_object_or_404(User, id=selected_customer_id, role='cliente')
        orders = Order.objects.filter(
            user=selected_customer
        ).prefetch_related(
            'details__product',
            'details__color_product__general_color'
        ).order_by('-order_date')

    return render(request, 'order/customer_orders_panel.html', {
        'customers': customers,
        'selected_customer': selected_customer,
        'orders': orders,
    })