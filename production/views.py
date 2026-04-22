from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Case, When, IntegerField, Prefetch
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone

from .models import (
    ProductionTask,
    EmployeeInventory,
    SupplyTask,
    SupplyColorProduct,
    Supply,
)
from account.models import User
from account.views import require_role
from product.models import Product, ColorProduct
from order.models import Order, OrderDetail


@require_role('empleada')
def view_employee_information(request):
    """Rf-31 — Muestra el panel del empleado"""
    return render(request, 'production/employee.html')


@require_role('administrador')
def display_manufacturing_process(request):
    """Rf-34 — Muestra el panel de producción con tareas, filtros y pedidos confirmados"""
    employees = User.objects.filter(role='empleada')
    products = Product.objects.filter(active=True).prefetch_related('colors__general_color')

    order_detail_id = request.GET.get('order_detail')
    preselected_detail = None
    if order_detail_id:
        preselected_detail = get_object_or_404(
            OrderDetail.objects.select_related(
                'product', 'color_product__general_color', 'order'
            ),
            id=order_detail_id
        )

    filter_employee = request.GET.get('filter_employee', '')
    filter_status = request.GET.get('filter_status', '')

    tasks = ProductionTask.objects.select_related(
        'employee',
        'product__product',
        'product__general_color',
        'order_detail__order'
    )
    if filter_employee:
        tasks = tasks.filter(employee_id=filter_employee)
    if filter_status:
        tasks = tasks.filter(status=filter_status)

    tasks = tasks.annotate(
        status_order=Case(
            When(status='En progreso', then=0),
            When(status='Pendiente', then=1),
            When(status='Completada', then=2),
            When(status='Cancelada', then=3),
            default=4,
            output_field=IntegerField()
        )
    ).order_by('status_order', '-assignment_date')

    pending_orders = Order.objects.filter(
        status='Confirmado'
    ).prefetch_related(
        'details__product',
        'details__color_product__general_color'
    )

    return render(request, 'production/production_panel.html', {
        'employees': employees,
        'products': products,
        'preselected_detail': preselected_detail,
        'tasks': tasks,
        'filter_employee': filter_employee,
        'filter_status': filter_status,
        'status_choices': ProductionTask.STATUS,
        'pending_orders': pending_orders,
    })


def notify_employee_of_assignment(employee, color_product, order_detail, specification):
    """Rf-18 — Notifica al empleado por correo cuando se le asigna una tarea."""
    if not employee.email:
        return
    send_mail(
        subject='Nueva tarea asignada - Akima',
        message=(
            f'Hola {employee.first_name},\n\n'
            f'Se te ha asignado una nueva tarea de producción:\n'
            f'Producto: {color_product.product.name} — {color_product.general_color.name}\n'
            f'{"Especificación: " + specification + chr(10) if specification else ""}'
            f'{"Orden relacionada: #" + str(order_detail.order.id) + chr(10) if order_detail else ""}'
            f'\nPor favor ingresa al sistema para ver los detalles.\n\nAkima'
        ),
        from_email=None,
        recipient_list=[employee.email],
        fail_silently=True,
    )


@require_role('administrador')
def assign_products_to_employees(request):
    """Rf-25 — Asigna un producto a un empleado creando una tarea de producción."""
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        color_product_id = request.POST.get('color_product_id')
        order_detail_id = request.POST.get('order_detail_id') or None
        specification = request.POST.get('specification', '').strip()

        if not employee_id or not color_product_id:
            messages.error(request, 'Debes seleccionar una empleada y un producto.')
            return redirect('production_panel')

        employee = get_object_or_404(User, id=employee_id, role='empleada')
        color_product = get_object_or_404(ColorProduct, id=color_product_id)
        order_detail = None
        if order_detail_id:
            order_detail = get_object_or_404(OrderDetail, id=order_detail_id)

        ProductionTask.objects.create(
            employee=employee,
            product=color_product,
            order_detail=order_detail,
            specification=specification,
            status='Pendiente'
        )

        notify_employee_of_assignment(employee, color_product, order_detail, specification)

        messages.success(request, f'Tarea asignada a {employee.first_name} exitosamente.')
    return redirect('production_panel')


@require_role('empleada')
def view_assigned_products(request):
    user_id = request.session.get('user_id')
    employee = get_object_or_404(User, id=user_id, role='empleada')

    tasks = ProductionTask.objects.select_related(
        'employee',
        'product__product',
        'product__general_color',
        'order_detail__order',
        'order_detail__product',
        'order_detail__color_product__general_color',
    ).prefetch_related(
        Prefetch(
            'supplies',
            queryset=SupplyTask.objects.select_related('supply')
        ),
        Prefetch(
            'product__required_supplies',
            queryset=SupplyColorProduct.objects.select_related('supply')
        )
    ).filter(
        employee=employee
    ).annotate(
        status_order=Case(
            When(status='En progreso', then=0),
            When(status='Pendiente', then=1),
            When(status='Completada', then=2),
            When(status='Cancelada', then=3),
            default=4,
            output_field=IntegerField()
        )
    ).order_by('status_order', '-assignment_date')

    inventory = EmployeeInventory.objects.filter(
        employee=employee
    ).select_related('supply')

    inventory_dict = {
        inv.supply.id: inv.available_quantity for inv in inventory
    }

    for task in tasks:
        task.required_supplies_with_inventory = []

        for required in task.product.required_supplies.all():
            available_quantity = inventory_dict.get(required.supply.id, 0)

            task.required_supplies_with_inventory.append({
                'required': required,
                'available_quantity': available_quantity,
            })

        task.available_inventory_supplies = [
            inv for inv in inventory if inv.available_quantity > 0
        ]

        for supply_task in task.supplies.all():
            supply_task.used_quantity = (
                supply_task.initial_quantity - supply_task.final_quantity
            )

    # All supplies available for adding to inventory
    all_supplies = Supply.objects.select_related('general_color').order_by('type_supply', 'brand')

    return render(request, 'production/employee_panel.html', {
        'employee': employee,
        'tasks': tasks,
        'inventory': inventory,
        'all_supplies': all_supplies,
    })


def _parse_decimal(value):
    try:
        cleaned_value = str(value).strip().replace(',', '.')
        return Decimal(cleaned_value)
    except (InvalidOperation, AttributeError, TypeError):
        return None


# ──────────────────────────────────────────────────────────────────────────────
# RF-INV1: Agregar insumos al inventario personal (< 5 segundos)
# ──────────────────────────────────────────────────────────────────────────────

@require_role('empleada')
@transaction.atomic
def add_supply_to_inventory(request):
    """
    RF-INV1 — El empleado agrega insumos y cantidades a su inventario personal.
    Responde con JSON en menos de 5 segundos.

    Reglas de validación:
    - supply_id obligatorio y debe existir.
    - quantity obligatoria, numérica, mayor a 0, no negativa.
    - quantity no puede exceder 99 999.99 g.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)

    user_id = request.session.get('user_id')
    employee = get_object_or_404(User, id=user_id, role='empleada')

    supply_id = request.POST.get('supply_id', '').strip()
    raw_quantity = request.POST.get('quantity', '').strip()

    # ── Validaciones ──────────────────────────────────────────────────────────
    if not supply_id:
        return JsonResponse(
            {'success': False, 'error': 'Debes seleccionar un insumo.'},
            status=400
        )

    if not raw_quantity:
        return JsonResponse(
            {'success': False, 'error': 'Debes ingresar una cantidad.'},
            status=400
        )

    try:
        supply_id_int = int(supply_id)
    except (ValueError, TypeError):
        return JsonResponse(
            {'success': False, 'error': 'El insumo seleccionado no es válido.'},
            status=400
        )

    quantity = _parse_decimal(raw_quantity)

    if quantity is None:
        return JsonResponse(
            {'success': False, 'error': 'La cantidad debe ser un número válido (ej: 150 o 150.5).'},
            status=400
        )

    if quantity < Decimal('0.00'):
        return JsonResponse(
            {'success': False, 'error': 'La cantidad no puede ser negativa.'},
            status=400
        )

    if quantity == Decimal('0.00'):
        return JsonResponse(
            {'success': False, 'error': 'La cantidad debe ser mayor a 0.'},
            status=400
        )

    if quantity > Decimal('99999.99'):
        return JsonResponse(
            {'success': False, 'error': 'La cantidad ingresada supera el límite permitido (99 999.99 g).'},
            status=400
        )

    # ── Lógica ────────────────────────────────────────────────────────────────
    supply = get_object_or_404(Supply, id=supply_id_int)

    inventory, _ = EmployeeInventory.objects.select_for_update().get_or_create(
        employee=employee,
        supply=supply,
        defaults={'available_quantity': Decimal('0.00')}
    )

    inventory.available_quantity += quantity
    inventory.save()

    return JsonResponse({
        'success': True,
        'message': f'Se agregaron {quantity:f} g de "{supply}" al inventario.',
        'item': {
            'supply_id': supply.id,
            'supply_name': str(supply),
            'type_supply': supply.type_supply,
            'available_quantity': float(inventory.available_quantity),
            'last_update': inventory.last_update.strftime('%d/%m/%Y %H:%M'),
        }
    })


# ──────────────────────────────────────────────────────────────────────────────
# RF-19: Iniciar tarea registrando insumos iniciales
# ──────────────────────────────────────────────────────────────────────────────

@require_role('empleada')
@transaction.atomic
def start_task_supplies(request, task_id):
    """
    RF-19 — Registra la cantidad inicial de insumos al iniciar la producción.
    """
    if request.method != 'POST':
        return redirect('employee_panel')

    user_id = request.session.get('user_id')
    employee = get_object_or_404(User, id=user_id, role='empleada')

    task = get_object_or_404(
        ProductionTask.objects.select_related('employee', 'product__product', 'product__general_color'),
        id=task_id,
        employee=employee
    )

    if task.status != 'Pendiente':
        messages.error(request, 'Solo puedes iniciar tareas en estado Pendiente.')
        return redirect('employee_panel')

    required_supplies = list(
        SupplyColorProduct.objects.select_related('supply').filter(color_product=task.product)
    )

    if not required_supplies:
        messages.error(
            request,
            'Este producto no tiene insumos configurados. Contacta al administrador.'
        )
        return redirect('employee_panel')

    submitted_supplies = []
    errors = []

    for required in required_supplies:
        field_name = f'initial_quantity_{required.supply.id}'
        raw_value = request.POST.get(field_name)
        quantity = _parse_decimal(raw_value)

        if quantity is None:
            errors.append(f'La cantidad de "{required.supply}" debe ser un número válido.')
            continue

        if quantity < Decimal('0.00'):
            errors.append(f'La cantidad inicial de "{required.supply}" no puede ser negativa.')
            continue

        inventory = EmployeeInventory.objects.filter(
            employee=employee,
            supply=required.supply
        ).first()

        available_quantity = inventory.available_quantity if inventory else Decimal('0.00')

        if quantity > available_quantity:
            errors.append(
                f'No tienes suficiente inventario de "{required.supply}". '
                f'Disponible: {available_quantity} g'
            )
            continue

        submitted_supplies.append((required.supply, quantity))

    if errors:
        for error in errors:
            messages.error(request, error)
        return redirect('employee_panel')

    if task.supplies.exists():
        messages.error(request, 'Esta tarea ya tiene insumos iniciales registrados.')
        return redirect('employee_panel')

    for supply, quantity in submitted_supplies:
        SupplyTask.objects.create(
            task=task,
            supply=supply,
            initial_quantity=quantity,
            final_quantity=Decimal('0.00')
        )

    task.status = 'En progreso'
    task.initial_date = timezone.now()
    task.save()

    if task.order_detail:
        order = task.order_detail.order
        if order.status == 'Confirmado':
            order.status = 'En producción'
            order.save()

    messages.success(request, f'Tarea #{task.id} iniciada y suministros registrados exitosamente.')
    return redirect('employee_panel')


# ──────────────────────────────────────────────────────────────────────────────
# RF-20: Registrar sobrantes y actualizar inventario (< 3 segundos)
# ──────────────────────────────────────────────────────────────────────────────

@require_role('empleada')
@transaction.atomic
def finish_task_supplies(request, task_id):
    """
    RF-20 — Registra sobrantes y descuenta del inventario lo realmente consumido.
    Responde con JSON en menos de 3 segundos cuando la petición es AJAX.

    Reglas de validación:
    - Cantidad sobrante obligatoria y numérica.
    - Sobrante no puede ser negativo.
    - Sobrante no puede superar la cantidad inicial registrada.
    - El consumo resultante no puede exceder el inventario disponible.
    """
    if request.method != 'POST':
        return redirect('employee_panel')

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    user_id = request.session.get('user_id')
    employee = get_object_or_404(User, id=user_id, role='empleada')

    task = get_object_or_404(
        ProductionTask.objects.select_related('employee'),
        id=task_id,
        employee=employee
    )

    if task.status != 'En progreso':
        error_msg = 'Solo puedes finalizar tareas en estado En progreso.'
        if is_ajax:
            return JsonResponse({'success': False, 'errors': [error_msg]}, status=400)
        messages.error(request, error_msg)
        return redirect('employee_panel')

    task_supplies = list(
        SupplyTask.objects.select_related('supply').filter(task=task)
    )

    if not task_supplies:
        error_msg = 'Primero debes registrar los insumos iniciales de esta tarea.'
        if is_ajax:
            return JsonResponse({'success': False, 'errors': [error_msg]}, status=400)
        messages.error(request, error_msg)
        return redirect('employee_panel')

    parsed_leftovers = []
    errors = []

    for supply_task in task_supplies:
        field_name = f'final_quantity_{supply_task.id}'
        raw_value = request.POST.get(field_name)
        leftover = _parse_decimal(raw_value)

        if leftover is None:
            errors.append(
                f'La cantidad sobrante de "{supply_task.supply}" debe ser un número válido.'
            )
            continue

        if leftover < Decimal('0.00'):
            errors.append(
                f'La cantidad sobrante de "{supply_task.supply}" no puede ser negativa.'
            )
            continue

        if leftover > supply_task.initial_quantity:
            errors.append(
                f'La cantidad sobrante de "{supply_task.supply}" no puede ser mayor '
                f'a la cantidad inicial registrada ({supply_task.initial_quantity} g).'
            )
            continue

        parsed_leftovers.append((supply_task, leftover))

    if errors:
        if is_ajax:
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        for error in errors:
            messages.error(request, error)
        return redirect('employee_panel')

    updated_inventory = []

    for supply_task, leftover in parsed_leftovers:
        supply_task.final_quantity = leftover
        supply_task.save()

        consumed_quantity = supply_task.initial_quantity - leftover

        inventory = EmployeeInventory.objects.select_for_update().filter(
            employee=employee,
            supply=supply_task.supply
        ).first()

        if not inventory:
            error_msg = f'No existe inventario para el insumo "{supply_task.supply}".'
            if is_ajax:
                return JsonResponse({'success': False, 'errors': [error_msg]}, status=400)
            messages.error(request, error_msg)
            raise ValueError('Inventario no encontrado.')

        if consumed_quantity > inventory.available_quantity:
            error_msg = (
                f'El consumo calculado de "{supply_task.supply}" '
                f'excede el inventario disponible ({inventory.available_quantity} g).'
            )
            if is_ajax:
                return JsonResponse({'success': False, 'errors': [error_msg]}, status=400)
            messages.error(request, error_msg)
            raise ValueError('Consumo excede inventario disponible.')

        inventory.available_quantity -= consumed_quantity
        inventory.save()

        updated_inventory.append({
            'supply_id': supply_task.supply.id,
            'supply_name': str(supply_task.supply),
            'consumed': float(consumed_quantity),
            'remaining': float(inventory.available_quantity),
            'last_update': inventory.last_update.strftime('%d/%m/%Y %H:%M'),
        })

    task.status = 'Completada'
    task.final_date = timezone.now()
    task.save()

    if task.order_detail:
        order = task.order_detail.order
        all_tasks = ProductionTask.objects.filter(order_detail__order=order)
        all_completed = all(t.status == 'Completada' for t in all_tasks)
        if all_completed:
            order.status = 'Completado'
            order.save()

    success_msg = f'Tarea #{task.id} finalizada y sobrantes registrados exitosamente.'

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': success_msg,
            'task_id': task.id,
            'updated_inventory': updated_inventory,
        })

    messages.success(request, success_msg)
    return redirect('employee_panel')


@require_role('empleada')
@transaction.atomic
def add_supply_to_task(request, task_id):
    if request.method != 'POST':
        return redirect('employee_panel')

    user_id = request.session.get('user_id')
    employee = get_object_or_404(User, id=user_id, role='empleada')

    task = get_object_or_404(
        ProductionTask.objects.select_related('employee'),
        id=task_id,
        employee=employee
    )

    if task.status != 'En progreso':
        messages.error(request, 'Solo puedes agregar insumos a tareas en progreso.')
        return redirect('employee_panel')

    supply_id = request.POST.get('supply_id')
    raw_quantity = request.POST.get('initial_quantity')

    if not supply_id or not raw_quantity:
        messages.error(request, 'Debes seleccionar un insumo y una cantidad.')
        return redirect('employee_panel')

    supply = get_object_or_404(Supply, id=supply_id)
    quantity = _parse_decimal(raw_quantity)

    if quantity is None or quantity <= Decimal('0.00'):
        messages.error(request, 'La cantidad debe ser mayor a 0.')
        return redirect('employee_panel')

    inventory = EmployeeInventory.objects.filter(
        employee=employee,
        supply=supply
    ).first()

    available_quantity = inventory.available_quantity if inventory else Decimal('0.00')

    if quantity > available_quantity:
        messages.error(
            request,
            f'No tienes suficiente inventario de {supply}. Disponible: {available_quantity}'
        )
        return redirect('employee_panel')

    existing_supply_task = SupplyTask.objects.filter(
        task=task,
        supply=supply
    ).first()

    if existing_supply_task:
        existing_supply_task.initial_quantity += quantity
        existing_supply_task.save()
        messages.success(
            request,
            f'Se sumaron {quantity} al insumo en la tarea #{task.id}.'
        )
    else:
        SupplyTask.objects.create(
            task=task,
            supply=supply,
            initial_quantity=quantity,
            final_quantity=Decimal('0.00')
        )
        messages.success(request, f'Insumo agregado a la tarea #{task.id} exitosamente.')

    return redirect('employee_panel')