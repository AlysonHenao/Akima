from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

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

    tasks = tasks.order_by(
        'status',
        '-assignment_date'
    )

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
        quantity = int(request.POST.get('quantity', 1))
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
            quantity=quantity,
            order_detail=order_detail,
            final_date=final_date,
            specification=specification,
            status='Pendiente'
        )
        messages.success(request, f'Tarea asignada a {employee.first_name} exitosamente.')
    return redirect('production_panel')