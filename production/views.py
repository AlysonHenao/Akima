from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Case, When, IntegerField, Prefetch
from django.db import transaction
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


# NUEVA FUNCIÓN (CONSULT MANUFACTURING INFO)
@require_role('administrador')
def consult_manufacturing_information(request):
    tasks = ProductionTask.objects.select_related(
        'employee',
        'product__product',
        'product__general_color',
        'order_detail__order'
    ).prefetch_related(
        'supplies__supply'
    ).order_by('-assignment_date')

    supplies = Supply.objects.all()

    inventory = EmployeeInventory.objects.select_related(
        'employee', 'supply'
    )

    return render(request, 'production/consult_manufacturing.html', {
        'tasks': tasks,
        'supplies': supplies,
        'inventory': inventory,
    })


@require_role('empleada')
def view_employee_information(request):
    user_id = request.session.get('user_id')
    employee = get_object_or_404(User, id=user_id, role='empleada')

    inventory = EmployeeInventory.objects.filter(
        employee=employee
    ).select_related('supply')

    tasks_count = ProductionTask.objects.filter(employee=employee).count()

    return render(request, 'production/employee.html', {
        'employee': employee,
        'inventory': inventory,
        'tasks_count': tasks_count,
    })


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


def notify_employee_of_assignment(employee, color_product, order_detail, specification):
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
            f'\nPor favor ingresa al sistema.\n\nAkima'
        ),
        from_email=None,
        recipient_list=[employee.email],
        fail_silently=True,
    )


@require_role('administrador')
def assign_products_to_employees(request):
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
    ).order_by('-assignment_date')

    return render(request, 'production/employee_panel.html', {
        'employee': employee,
        'tasks': tasks,
    })
def _parse_decimal(value):
    try:
        cleaned_value = str(value).strip().replace(',', '.')
        return Decimal(cleaned_value)
    except (InvalidOperation, AttributeError, TypeError):
        return None


@require_role('empleada')
@transaction.atomic
def start_task_supplies(request, task_id):
    if request.method != 'POST':
        return redirect('employee_panel')

    user_id = request.session.get('user_id')
    employee = get_object_or_404(User, id=user_id, role='empleada')

    task = get_object_or_404(ProductionTask, id=task_id, employee=employee)

    if task.status != 'Pendiente':
        messages.error(request, 'Solo puedes iniciar tareas en estado Pendiente.')
        return redirect('employee_panel')

    task.status = 'En progreso'
    task.initial_date = timezone.now()
    task.save()

    messages.success(request, f'Tarea #{task.id} iniciada.')
    return redirect('employee_panel')


@require_role('empleada')
@transaction.atomic
def finish_task_supplies(request, task_id):
    if request.method != 'POST':
        return redirect('employee_panel')

    user_id = request.session.get('user_id')
    employee = get_object_or_404(User, id=user_id, role='empleada')

    task = get_object_or_404(ProductionTask, id=task_id, employee=employee)

    if task.status != 'En progreso':
        messages.error(request, 'Solo puedes finalizar tareas en progreso.')
        return redirect('employee_panel')

    task.status = 'Completada'
    task.final_date = timezone.now()
    task.save()

    messages.success(request, f'Tarea #{task.id} finalizada.')
    return redirect('employee_panel')


@require_role('empleada')
@transaction.atomic
def add_supply_to_task(request, task_id):
    messages.success(request, 'Función de insumos ejecutada.')
    return redirect('employee_panel')    