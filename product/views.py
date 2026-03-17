from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal

from .models import Product, ColorProduct, ProductImage, GeneralColor, SetProduct
from order.models import OrderDetail


def home(request):
    products = Product.objects.filter(active=True)
    return render(request, 'product/home.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.prefetch_related('colors__general_color', 'images'),
        id=product_id,
        active=True
    )
    available_colors = product.colors.filter(available=True).select_related('general_color')
    sizes = [code for code, _ in OrderDetail.SIZE]
    return render(request, 'product/product_detail.html', {
        'product': product,
        'available_colors': available_colors,
        'sizes': sizes,
    })


def administrator(request):
    products = Product.objects.all()
    return render(request, 'product/administrator.html', {'products': products})


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
            for color_id in request.POST.getlist('colors'):
                ColorProduct.objects.create(
                    product=product,
                    general_color_id=color_id,
                    available=True
                )
            for image in request.FILES.getlist('images')[:5]:
                ProductImage.objects.create(
                    product=product,
                    url_image=image
                )
            if product.category == 'Set':
                for product_id in request.POST.getlist('set_products'):
                    quantity = request.POST.get(f'set_quantity_{product_id}')
                    price = request.POST.get(f'set_price_{product_id}')
                    if quantity and price:
                        SetProduct.objects.create(
                            set_product=product,
                            individual_product_id=product_id,
                            quantity=int(quantity),
                            set_price=Decimal(price)
                        )
            messages.success(request, f'¡Producto "{product.name}" creado exitosamente!')
            return redirect('new_product')
        except Exception as e:
            messages.error(request, f'Error al crear producto: {str(e)}')

    context = {
        'products': Product.objects.all().prefetch_related(
            'colors__general_color', 'images', 'set_components__individual_product'
        ),
        'colors': GeneralColor.objects.all().order_by('name'),
        'individual_products': Product.objects.exclude(category='Set').filter(active=True)
    }
    return render(request, 'product/new_product.html', context)


def toggle_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.active = not product.active
    product.save()
    state = "activado" if product.active else "desactivado"
    messages.success(request, f'Producto "{product.name}" {state}.')
    return redirect('new_product')

def create_color(request):
    if request.method == 'POST':
        nombre = request.POST.get('name', '').strip()
        if not nombre:
            messages.error(request, 'El nombre del color no puede estar vacío.')
            return redirect('new_product')
        color, created = GeneralColor.objects.get_or_create(name=nombre)
        if not created:
            messages.warning(request, f'El color "{nombre}" ya existe.')
        else:
            messages.success(request, f'Color "{nombre}" agregado exitosamente.')
    return redirect('new_product')