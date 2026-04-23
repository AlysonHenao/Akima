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
from product.models import Product, ColorProduct, GeneralColor
from order.models import Order, OrderDetail


# ─────────────────────────────────────────────────────────────
# CONSULT MANUFACTURING INFO
# ─────────────────────────────────────────────────────────────
@require_role('administrador')
def consult_manufacturing_information(request):
    tasks = ProductionTask.objects.select_related(
        'employee',
        'product__product',
        'product__general_color',
        'order_detail__order'
    ).prefetch_related('supplies__supply').order_by('-assignment_date')

    supplies = Supply.objects.all()

    inventory = EmployeeInventory.objects.select_related('employee', 'supply')

    return render(request, 'production/consult_manufacturing.html', {
        'tasks': tasks,
        'supplies': supplies,
        'inventory': inventory,
    })


# ─────────────────────────────────────────────────────────────
# VIEW EMPLOYEE INFO
# ─────────────────────────────────────────────────────────────
@require_role('empleada')
def view_employee_information(request):
    user_id = request.session.get('user_id')
    employee = get_object_or_404(User, id=user_id, role='empleada')

    inventory = EmployeeInventory.objects.filter(employee=employee).select_related('supply')
    tasks_count = ProductionTask.objects.filter(employee=employee).count()

    return render(request, 'production/employee.html', {
        'employee': employee,
        'inventory': inventory,
        'tasks_count': tasks_count,
    })


# ─────────────────────────────────────────────────────────────
# EMPLOYEE PROFILE (NUEVO)
# ─────────────────────────────────────────────────────────────
@require_role('empleada')
def view_employee_profile(request):
    user_id = request.session.get('user_id')
    employee = get_object_or_404(User, id=user_id, role='empleada')

    return render(request, 'production/employee_profile.html', {
        'employee': employee,
    })


# ─────────────────────────────────────────────────────────────
# PANEL ADMIN
# ─────────────────────────────────────────────────────────────
@require_role('administrador')
def display_manufacturing_process(request):
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


# ─────────────────────────────────────────────────────────────
# NOTIFICACIÓN
# ─────────────────────────────────────────────────────────────
def notify_employee_of_assignment(employee, color_product, order_detail, specification):
    if not employee.email:
        return

    send_mail(
        subject='Nueva tarea asignada - Akima',
        message=(
            f'Hola {employee.first_name},\n\n'
            f'Producto: {color_product.product.name} — {color_product.general_color.name}\n'
            f'{"Especificación: " + specification + chr(10) if specification else ""}'
            f'{"Orden: #" + str(order_detail.order.id) + chr(10) if order_detail else ""}'
        ),
        from_email=None,
        recipient_list=[employee.email],
        fail_silently=True,
    )


# ─────────────────────────────────────────────────────────────
# ASIGNAR TAREA
# ─────────────────────────────────────────────────────────────
@require_role('administrador')
def assign_products_to_employees(request):
    if request.method == 'POST':
        employee = get_object_or_404(User, id=request.POST.get('employee_id'), role='empleada')
        color_product = get_object_or_404(ColorProduct, id=request.POST.get('color_product_id'))

        order_detail_id = request.POST.get('order_detail_id')
        order_detail = OrderDetail.objects.filter(id=order_detail_id).first()

        ProductionTask.objects.create(
            employee=employee,
            product=color_product,
            order_detail=order_detail,
            specification=request.POST.get('specification', ''),
            status='Pendiente'
        )

        notify_employee_of_assignment(employee, color_product, order_detail, '')

        messages.success(request, 'Tarea asignada correctamente.')

    return redirect('production_panel')


# ─────────────────────────────────────────────────────────────
# PANEL EMPLEADA (MEJORADO CON GUÍA DE FABRICACIÓN)
# ─────────────────────────────────────────────────────────────
@require_role('empleada')
def view_assigned_products(request):
    employee = get_object_or_404(User, id=request.session.get('user_id'), role='empleada')

    tasks = ProductionTask.objects.filter(employee=employee).select_related(
        'product__product',
        'product__general_color'
    ).prefetch_related(
        'supplies__supply',
        'product__required_supplies__supply'
    ).order_by('-assignment_date')

    inventory = EmployeeInventory.objects.filter(employee=employee).select_related('supply')

    return render(request, 'production/employee_panel.html', {
        'employee': employee,
        'tasks': tasks,
        'inventory': inventory,
    })

# ─────────────────────────────────────────────────────────────
# PARSE DECIMAL
# ─────────────────────────────────────────────────────────────
def _parse_decimal(value):
    try:
        return Decimal(str(value).replace(',', '.'))
    except:
        return None


# ─────────────────────────────────────────────────────────────
# INVENTARIO
# ─────────────────────────────────────────────────────────────
@require_role('empleada')
@transaction.atomic
def add_supply_to_inventory(request):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)

    employee = get_object_or_404(User, id=request.session.get('user_id'), role='empleada')

    supply = get_object_or_404(Supply, id=request.POST.get('supply_id'))
    quantity = _parse_decimal(request.POST.get('quantity'))

    inventory, _ = EmployeeInventory.objects.get_or_create(
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


# ─────────────────────────────────────────────────────────────
# INICIAR TAREA
# ─────────────────────────────────────────────────────────────
@require_role('empleada')
@transaction.atomic
def start_task_supplies(request, task_id):
    employee = get_object_or_404(User, id=request.session.get('user_id'), role='empleada')
    task = get_object_or_404(ProductionTask, id=task_id, employee=employee)

    task.status = 'En progreso'
    task.initial_date = timezone.now()
    task.save()

    messages.success(request, 'Tarea iniciada.')
    return redirect('employee_panel')


# ─────────────────────────────────────────────────────────────
# FINALIZAR TAREA
# ─────────────────────────────────────────────────────────────
@require_role('empleada')
@transaction.atomic
def finish_task_supplies(request, task_id):
    employee = get_object_or_404(User, id=request.session.get('user_id'), role='empleada')
    task = get_object_or_404(ProductionTask, id=task_id, employee=employee)

    task.status = 'Completada'
    task.final_date = timezone.now()
    task.save()

    messages.success(request, 'Tarea finalizada.')
    return redirect('employee_panel')


# ─────────────────────────────────────────────────────────────
# AGREGAR INSUMO A TAREA
# ─────────────────────────────────────────────────────────────
@require_role('empleada')
def add_supply_to_task(request, task_id):
    messages.success(request, 'Insumo agregado.')
    return redirect('employee_panel')


@require_role('empleada')
def view_inventory(request):
    user_id = request.session.get('user_id')
    employee = get_object_or_404(User, id=user_id, role='empleada')

    inventory = EmployeeInventory.objects.filter(
        employee=employee
    ).select_related('supply').order_by('supply__type_supply', 'supply__brand')

    all_supplies = Supply.objects.all().order_by('type_supply', 'brand')

    return render(request, 'production/inventory.html', {
        'employee': employee,
        'inventory': inventory,
        'all_supplies': all_supplies,
    })


@require_role('empleada')
@transaction.atomic
def create_supply(request):
    if request.method != 'POST':
        return redirect('view_inventory')

    type_supply = request.POST.get('type_supply', '').strip()
    brand = request.POST.get('brand', '').strip()
    reference = request.POST.get('reference', '').strip()

    if not brand or not reference:
        messages.error(request, 'Marca y referencia son obligatorias.')
        return redirect('view_inventory')

    duplicate = Supply.objects.filter(
        type_supply=type_supply,
        brand__iexact=brand,
        reference__iexact=reference,
    ).first()

    if duplicate:
        messages.error(request, f'El insumo ya existe: {duplicate}')
        return redirect('view_inventory')

    Supply.objects.create(
        type_supply=type_supply,
        brand=brand,
        reference=reference,
        quantity=Decimal('0.00'),
        price=Decimal('0.00'),
    )

    messages.success(request, 'Insumo creado correctamente.')
    return redirect('view_inventory')

@require_role('administrador')
def employees_info(request):
    employees = User.objects.filter(role='empleada').order_by('first_name')

    selected_id = request.GET.get('employee_id')

    employee = None
    inventory = []
    tasks = []

    if selected_id:
        employee = get_object_or_404(User, id=selected_id, role='empleada')

        inventory = EmployeeInventory.objects.filter(
            employee=employee
        ).select_related('supply')

        tasks = ProductionTask.objects.filter(
            employee=employee
        ).select_related(
            'product__product',
            'product__general_color'
        ).order_by('-assignment_date')

    return render(request, 'production/employees_info.html', {
        'employees': employees,
        'employee': employee,
        'inventory': inventory,
        'tasks': tasks,
    })    