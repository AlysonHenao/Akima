from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from decimal import Decimal

from .models import Product, ColorProduct, ProductImage, GeneralColor, SetProduct
from order.models import OrderDetail
from account.views import require_role



def display_product_catalog(request):
    query = request.GET.get('q', '').strip()
    color_filter = request.GET.get('color', '').strip()
    category_filter = request.GET.get('category', '').strip()

    products = Product.objects.filter(active=True).prefetch_related('colors__general_color')

    if query:
        products = products.filter(name__icontains=query)

    if color_filter:
        products = products.filter(
            colors__general_color__name__iexact=color_filter,
            colors__available=True
        ).distinct()

    if category_filter:
        products = products.filter(category=category_filter)

    all_colors = GeneralColor.objects.order_by('name')
    categories = [{'value': v, 'label': l} for v, l in Product.CATEGORIES]

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'product/home.html', {
        'products': page_obj,
        'page_obj': page_obj,
        'query': query,
        'color_filter': color_filter,
        'category_filter': category_filter,
        'all_colors': all_colors,
        'categories': categories,
    })



def show_product_details(request, product_id):
    """Rf-04 — Muestra el detalle de un producto con colores y tallas disponibles"""
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



@require_role('administrador')
def administrator(request):
    """Soporte — Panel de administración general de productos"""
    products = Product.objects.all()
    return render(request, 'product/administrator.html', {'products': products})



def customize_product(product, post_data, files):
    """Rf-05 — Agrega colores, imágenes y composición de set a un producto."""
    for color_id in post_data.getlist('colors'):
        ColorProduct.objects.create(
            product=product,
            general_color_id=color_id,
            available=True
        )

    images = files.getlist('images')

    if len(images) > 5:
        raise Exception("Solo puedes subir máximo 5 imágenes")

    if product.images.count() + len(images) > 5:
        raise Exception("El producto no puede tener más de 5 imágenes en total")

    for image in images:
        ProductImage.objects.create(product=product, url_image=image)

    if product.category == 'Set':
        for product_id in post_data.getlist('set_products'):
            quantity = post_data.get(f'set_quantity_{product_id}')
            price = post_data.get(f'set_price_{product_id}')

            if quantity and price:
                price = price.replace(',', '.')

                SetProduct.objects.create(
                    set_product=product,
                    individual_product_id=product_id,
                    quantity=int(quantity),
                    set_price=Decimal(price)
                )



@require_role('administrador')
def create_product(request):
    if request.method == 'POST':
        try:
            price = request.POST.get('price', '0').replace(',', '.')

            product = Product.objects.create(
                name=request.POST.get('name'),
                category=request.POST.get('category'),
                description=request.POST.get('description'),
                price=Decimal(price),
                stock=int(request.POST.get('stock', 0)),
                manufacturing_time=int(request.POST.get('manufacturing_time')),
                active=request.POST.get('active') == 'on',
                manufacturing_guide=request.FILES.get('manufacturing_guide'),
                size_guide=request.FILES.get('size_guide'),
            )

            customize_product(product, request.POST, request.FILES)

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



@require_role('administrador')
def edit_product(request, product_id):
    product = get_object_or_404(
        Product.objects.prefetch_related('colors__general_color', 'images'),
        id=product_id
    )

    if request.method == 'POST':
        try:
            price = request.POST.get('price', '0').replace(',', '.')

            product.name = request.POST.get('name')
            product.category = request.POST.get('category')
            product.description = request.POST.get('description')
            product.price = Decimal(price)
            product.stock = int(request.POST.get('stock', 0))
            product.manufacturing_time = int(request.POST.get('manufacturing_time'))
            product.active = request.POST.get('active') == 'on'

            if request.FILES.get('manufacturing_guide'):
                product.manufacturing_guide = request.FILES.get('manufacturing_guide')

            if request.FILES.get('size_guide'):
                product.size_guide = request.FILES.get('size_guide')

            product.save()

            color_ids_nuevos = set(int(x) for x in request.POST.getlist('colors'))
            color_ids_actuales = set(
                product.colors.values_list('general_color_id', flat=True)
            )

            for color_id in color_ids_nuevos - color_ids_actuales:
                ColorProduct.objects.create(
                    product=product,
                    general_color_id=color_id,
                    available=True
                )

            product.colors.filter(
                general_color_id__in=color_ids_actuales - color_ids_nuevos
            ).delete()

            
            ids_a_eliminar = request.POST.getlist('delete_images')
            if ids_a_eliminar:
                ProductImage.objects.filter(
                    id__in=ids_a_eliminar,
                    product=product
                ).delete()

            new_images = request.FILES.getlist('new_images')

            if product.images.count() + len(new_images) > 5:
                raise Exception("Máximo 5 imágenes por producto")

            for image in new_images:
                ProductImage.objects.create(product=product, url_image=image)

            messages.success(request, f'Producto "{product.name}" actualizado correctamente.')

        except Exception as e:
            messages.error(request, f'Error al editar producto: {str(e)}')

    return redirect('new_product')


def toggle_product(request, product_id):
    """Rf-29 (soporte) — Activa o desactiva un producto rápidamente desde el listado"""
    product = get_object_or_404(Product, id=product_id)
    product.active = not product.active
    product.save()
    state = "activado" if product.active else "desactivado"
    messages.success(request, f'Producto "{product.name}" {state}.')
    return redirect('new_product')



def create_general_color(request):
    """Rf-28 (soporte) — Crea un nuevo color en el catálogo general"""
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