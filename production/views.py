from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Case, When, IntegerField

from .models import ProductionTask, EmployeeInventory
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
    """Rf-18 — Notifica al empleado por correo cuando se le asigna una tarea.
    Función interna llamada desde assign_products_to_employees (Rf-25)."""
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
    """Rf-25 — Asigna un producto a un empleado creando una tarea de producción.
    Tras asignar llama a notify_employee_of_assignment (Rf-18) para notificar."""
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

        existing_task = ProductionTask.objects.filter(
            employee=employee,
            product=color_product,
            status__in=['Pendiente', 'En progreso']
        ).exists()

        if existing_task:
            messages.error(
                request,
                f'{employee.first_name} ya tiene asignada esta tarea en estado Pendiente o En progreso.'
            )
            return redirect('production_panel')

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

    return render(request, 'production/employee_panel.html', {
        'employee': employee,
        'tasks': tasks,
    })
