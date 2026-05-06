from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Order, OrderDetail, ShoppingCart, ItemCart,
    PaymentMethod, PaymentReceipt, FinancialMovement, FinancialMovementSupply, User
)
from product.models import Product, ColorProduct
from production.models import Supply
from account.views import require_role


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    user_id = request.session.get('user_id')
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            cart, created = ShoppingCart.objects.get_or_create(
                user=user,
                defaults={'session_key': session_key}
            )
            cart.session_key = session_key
            cart.save()
            return cart
        except User.DoesNotExist:
            pass
    
    cart, created = ShoppingCart.objects.get_or_create(session_key=session_key)
    return cart


def add_product_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, active=True)
        color_id = request.POST.get('color')
        size = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            messages.error(request, 'La cantidad debe ser mayor a 0.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

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

    if nueva_cantidad <= 0:
        messages.error(request, 'La cantidad debe ser mayor a 0.')
        return redirect(next_url + '?carrito=abierto')
    
    item.quantity = nueva_cantidad
    item.save()

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


def display_payment_methods(cart, items):
    return {
        'items': items,
        'total': cart.formatted_total,
        'payment_methods': PaymentMethod.objects.filter(active=True),
    }


def place_order(cart, items, user=None):
    total = cart.get_total()
    order_user = cart.user or user
    
    order = Order.objects.create(
        user=order_user,
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
    cart.items.all().delete()
    return order


def upload_payment_proof(order, payment_method, receipt_file):
    PaymentReceipt.objects.create(
        order=order,
        payment_method=payment_method,
        receipt=receipt_file,
        amount=order.total,
    )


def notify_administrator_of_payment(order, payment_method):
    cliente_nombre = (
        f"{order.user.first_name} {order.user.last_name}"
        if order.user else "Cliente invitado"
    )
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


def payment_page(request):
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para realizar un pedido.')
        return redirect('login')

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

        user_id = request.session.get('user_id')
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

        try:
            order = place_order(cart, items, user=user)
            upload_payment_proof(order, payment_method, receipt_file)
            notify_administrator_of_payment(order, payment_method)

            messages.success(request, '¡Comprobante enviado! Tu pedido será verificado.')
            return redirect('home')
        except ValueError as e:
            messages.error(request, f'Error al procesar pedido: {str(e)}')
            return redirect('payment')

    context = display_payment_methods(cart, items)
    return render(request, 'order/payment.html', context)


@require_role('administrador')
def view_order_information(request):
    all_orders = Order.objects.select_related('user').prefetch_related(
        'receipts__payment_method',
        'details__product',
        'details__color_product__general_color'
    ).order_by('-order_date')
    return render(request, 'order/orders.html', {'orders': all_orders})


def notify_customer_of_order(order):
    if order.user and order.user.email:
        send_mail(
            subject=f'Pedido #{order.id} confirmado - Akima',
            message=(
                f'Hola {order.user.first_name},\n\n'
                f'Tu pago ha sido confirmado.\n'
                f'Total: ${order.total}\n\n'
                f'Gracias por comprar en Akima.'
            ),
            from_email=None,
            recipient_list=[order.user.email],
            fail_silently=True,
        )


def confirm_payment(request, receipt_id):
    if request.session.get('user_role') != 'administrador':
        messages.error(request, 'No tienes permiso para acceder a esta acción.')
        return redirect('login')

    if request.method == 'POST':
        receipt = get_object_or_404(PaymentReceipt, id=receipt_id)
        receipt.confirm = True
        receipt.confirm_date = timezone.now()
        receipt.save()

        order = receipt.order
        order.status = 'Confirmado'
        order.save()

        notify_customer_of_order(order)

        messages.success(request, f'Pago del pedido #{order.id} confirmado exitosamente.')

    return redirect('orders')


@require_role('administrador')
def modify_order_status(request, order_id):
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


@require_role('administrador', 'empleada', 'cliente')
def check_order_status(request):
    user_role = request.session.get('user_role')
    user_id = request.session.get('user_id')

    if user_role in ['cliente', 'empleada', 'administrador']:
        orders = Order.objects.filter(
            user_id=user_id
        ).prefetch_related(
            'details__product',
            'details__color_product__general_color'
        ).order_by('-order_date')

        return render(request, 'order/customer_orders_panel.html', {
            'orders': orders,
            'is_cliente': True,
        })


@require_role('administrador')
def register_financial_movement(request):

    employees = User.objects.filter(role='empleada')
    orders = Order.objects.all().order_by('-id')
    supplies = Supply.objects.all().order_by('brand')

    if request.method == 'POST':

        movement_id = request.POST.get('movement_id')

        movement_type = request.POST.get('type')
        category = request.POST.get('category')
        concept = request.POST.get('concept')
        amount = request.POST.get('amount')
        note = request.POST.get('note')
        receipt = request.FILES.get('receipt')

        order_id = request.POST.get('order')
        employee_id = request.POST.get('employee')

        if movement_id:
            movement = get_object_or_404(
                FinancialMovement,
                id=movement_id
            )
        else:
            movement = FinancialMovement()

        try:
            amount = int(amount)

            if amount % 100 != 0:
                messages.error(request, 'El monto debe subir de 100 en 100.')
                return redirect('register_financial_movement')
        except:
            messages.error(request, 'Monto inválido.')
            return redirect('register_financial_movement')

        movement.type = movement_type
        movement.category = category
        movement.concept = concept
        movement.amount = amount
        movement.note = note

        user_id = request.session.get('user_id')

        if user_id:
            movement.user = User.objects.get(id=user_id)

        if receipt:
            movement.receipt = receipt

        movement.order = None

        if category == 'Venta' and order_id:
            movement.order = Order.objects.get(id=order_id)

        movement.employee = None

        if category == 'Pago a empleados' and employee_id:
            movement.employee = User.objects.get(id=employee_id)

        movement.save()

        if category == 'Compra de insumos':

            FinancialMovementSupply.objects.filter(
                financial_movement=movement
            ).delete()

            supply_ids = request.POST.getlist('supply_id[]')
            quantities = request.POST.getlist('quantity[]')
            unit_costs = request.POST.getlist('unit_cost[]')

            for i in range(len(supply_ids)):

                if not supply_ids[i]:
                    continue

                supply = Supply.objects.get(id=supply_ids[i])

                FinancialMovementSupply.objects.create(
                    financial_movement=movement,
                    supply=supply,
                    quantity=int(quantities[i]),
                    unit_cost=int(unit_costs[i]),
                )

        if movement_id:
            messages.success(request, 'Movimiento actualizado.')
        else:
            messages.success(request, 'Movimiento registrado.')

        return redirect('register_financial_movement')

    movements = FinancialMovement.objects.select_related(
        'user',
        'order',
        'employee'
    ).prefetch_related(
        'supplies__supply'
    ).order_by('-movement_date')

    return render(
        request,
        'order/financial_movements.html',
        {
            'movements': movements,
            'categories': FinancialMovement.CATEGORIES,
            'types': FinancialMovement.TYPES,
            'employees': employees,
            'orders': orders,
            'supplies': supplies,
        }
    )