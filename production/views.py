from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Case, When, IntegerField


from .models import ProductionTask, EmployeeInventory
from account.models import User
from product.models import Product, ColorProduct
from order.models import Order, OrderDetail


def employee(request):
    return render(request, 'production/employee.html')


def production_panel(request):
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


def assign_task(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        color_product_id = request.POST.get('color_product_id')
        order_detail_id = request.POST.get('order_detail_id') or None
        final_date = request.POST.get('final_date') or None
        specification = request.POST.get('specification', '').strip()

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

        if employee.email:
            send_mail(
                subject=f'Nueva tarea asignada - Akima',
                message=(
                    f'Hola {employee.first_name},\n\n'
                    f'Se te ha asignado una nueva tarea de producción:\n'
                    f'Producto: {color_product.product.name} — {color_product.general_color.name}\n'
                    f'{"Especificación: " + specification + chr(10) if specification else ""}'
                    f'{"Orden relacionada: #" + str(order_detail.order.id) + chr(10) if order_detail else ""}'
                    f'\nPor favor ingresa al sistema para ver los detalles.\n\n'
                    f'Akima'
                ),
                from_email=None,
                recipient_list=[employee.email],
                fail_silently=True,
            )

        messages.success(request, f'Tarea asignada a {employee.first_name} exitosamente.')
    return redirect('production_panel')