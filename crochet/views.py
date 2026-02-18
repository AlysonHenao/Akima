from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import (
    Producto, ProductoColor, ProductoImagen, Pedido,
    ColorGeneral, SetProducto, PedidoDetalle,
    CarritoCompra, CarritoItem, MetodoPago, ComprobantePago,
)
from decimal import Decimal

def home(request):

    """Página principal - Muestra productos activos"""
    productos = Producto.objects.filter(activo=True)
    return render(request, 'home.html', {'productos': productos})

def payment(request):
    carrito = get_or_create_carrito(request)

    
    if request.method == "POST":
        comprobante = request.FILES.get("comprobante")

        if comprobante:
            messages.success(request, "Comprobante enviado correctamente. Tu pedido será verificado.")
            return redirect("home")

    
    items = carrito.items.select_related(
        'id_producto',
        'id_producto_color__id_color_general'
    )

    total = carrito.get_total()
    metodos_pago = MetodoPago.objects.filter(activo=True)

    return render(request, "payment_methods.html", {
        "items": items,
        "total": total,
        "metodos_pago": metodos_pago,
    })

def administrator(request):
    productos = Producto.objects.all()
    return render(request, 'administrator.html', {'productos': productos})

def new_product(request):
    """Panel de administración - Crear productos"""
    
    if request.method == 'POST':
        try:
            # 1. Crear el producto base
            producto = Producto.objects.create(
                nombre=request.POST.get('nombre'),
                categoria=request.POST.get('categoria'),
                descripcion=request.POST.get('descripcion'),
                precio=Decimal(request.POST.get('precio')),
                stock=int(request.POST.get('stock', 0)),
                tiempo_fabricacion=int(request.POST.get('tiempo_fabricacion')),
                activo=request.POST.get('activo') == 'on',
                guia_fabricacion=request.FILES.get('guia_fabricacion'),
                guia_tallas=request.FILES.get('guia_tallas'),
            )
            
            # 2. Agregar colores disponibles
            colores_ids = request.POST.getlist('colores')
            for color_id in colores_ids:
                ProductoColor.objects.create(
                    id_producto=producto,
                    id_color_general_id=color_id,
                    disponible=True
                )
            
            # 3. Agregar imágenes
            imagenes = request.FILES.getlist('imagenes')
            for imagen in imagenes[:5]:  # Máximo 5 imágenes
                ProductoImagen.objects.create(
                    id_producto=producto,
                    url_imagen=imagen
                )
            
            # 4. Si es Set, crear composición
            if producto.categoria == 'Set':
                productos_set_ids = request.POST.getlist('set_productos')
                
                for producto_id in productos_set_ids:
                    cantidad = request.POST.get(f'set_cantidad_{producto_id}')
                    precio = request.POST.get(f'set_precio_{producto_id}')
                    
                    if cantidad and precio:
                        SetProducto.objects.create(
                            id_producto_set=producto,
                            id_producto_individual_id=producto_id,
                            cantidad=int(cantidad),
                            precio_set=Decimal(precio)
                        )
            
            messages.success(request, f'¡Producto "{producto.nombre}" creado exitosamente!')
            return redirect('new_product')
            
        except Exception as e:
            messages.error(request, f'Error al crear producto: {str(e)}')
    
    # Obtener datos para el template
    context = {
        'productos': Producto.objects.all().prefetch_related(
            'colores__id_color_general', 
            'imagenes',
            'componentes_set__id_producto_individual'
        ),
        'colores': ColorGeneral.objects.all().order_by('nombre'),
        'productos_individuales': Producto.objects.exclude(categoria='Set').filter(activo=True)
    }
    
    return render(request, 'new_product.html', context)

def toggle_producto(request, producto_id):
    """Activar/desactivar producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    producto.activo = not producto.activo
    producto.save()
    
    estado = "activado" if producto.activo else "desactivado"
    messages.success(request, f'Producto "{producto.nombre}" {estado}.')
    
    return redirect('new_product')

def producto_detalle(request, producto_id):
    producto = get_object_or_404(
        Producto.objects.prefetch_related(
            'colores__id_color_general',
            'imagenes'
        ),
        id=producto_id,
        activo=True
    )

    colores_disponibles = producto.colores.filter(disponible=True).select_related('id_color_general')

    tallas = [codigo for codigo, _ in PedidoDetalle.TALLA]

    return render(request, 'producto_detalle.html', {
        'producto': producto,
        'colores_disponibles': colores_disponibles,
        'tallas': tallas,
    })


def employee(request):
    """Vista de empleados (por implementar)"""
    return render(request, 'employee.html')


def get_or_create_carrito(request):
    """Obtiene o crea un carrito para la sesión actual"""
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    carrito, created = CarritoCompra.objects.get_or_create(session_key=session_key)
    return carrito


def add_to_cart(request, producto_id):
    """Agrega un producto personalizado al carrito"""
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id, activo=True)
        
        color_id = request.POST.get('color')
        talla = request.POST.get('talla')
        cantidad = int(request.POST.get('cantidad', 1))
        
        producto_color = get_object_or_404(
            ProductoColor, 
            id=color_id, 
            id_producto=producto,
            disponible=True
        )
        
        carrito = get_or_create_carrito(request)
        
        item_existente = CarritoItem.objects.filter(
            id_carrito=carrito,
            id_producto=producto,
            id_producto_color=producto_color,
            talla=talla
        ).first()
        
        if item_existente:
            item_existente.cantidad += cantidad
            item_existente.save()
            messages.success(request, f'Se actualizó la cantidad de "{producto.nombre}" en el carrito.')
        else:
            CarritoItem.objects.create(
                id_carrito=carrito,
                id_producto=producto,
                id_producto_color=producto_color,
                talla=talla,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            messages.success(request, f'"{producto.nombre}" agregado al carrito exitosamente.')
        
        return redirect('view_cart')
    
    return redirect('home')


def view_cart(request):
    """Muestra el contenido del carrito"""
    carrito = get_or_create_carrito(request)
    items = carrito.items.select_related(
        'id_producto',
        'id_producto_color__id_color_general'
    ).prefetch_related('id_producto__imagenes')
    
    total = carrito.get_total()
    
    context = {
        'carrito': carrito,
        'items': items,
        'total': total,
    }
    
    return render(request, 'cart.html', context)


def update_cart_item(request, item_id):
    """Actualiza la cantidad de un item en el carrito"""
    if request.method == 'POST':
        carrito = get_or_create_carrito(request)
        item = get_object_or_404(CarritoItem, id=item_id, id_carrito=carrito)
        
        import json
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                nueva_cantidad = int(data.get('quantity', 1))
            except:
                nueva_cantidad = int(request.POST.get('cantidad', 1))
        else:
            nueva_cantidad = int(request.POST.get('cantidad', 1))
        
        if nueva_cantidad > 0:
            item.cantidad = nueva_cantidad
            item.save()
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'subtotal': float(item.get_subtotal()),
                    'cart_total': float(carrito.get_total())
                })
            messages.success(request, 'Cantidad actualizada.')
        else:
            item.delete()
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'deleted': True,
                    'cart_total': float(carrito.get_total())
                })
            messages.success(request, 'Producto eliminado del carrito.')
    
    return redirect('view_cart')


def remove_cart_item(request, item_id):
    """Elimina un item del carrito"""
    carrito = get_or_create_carrito(request)
    item = get_object_or_404(CarritoItem, id=item_id, id_carrito=carrito)
    
    nombre_producto = item.id_producto.nombre
    item.delete()
    
    messages.success(request, f'"{nombre_producto}" eliminado del carrito.')
    return redirect('view_cart')


def empty_cart(request):
    """Vacía todo el carrito"""
    carrito = get_or_create_carrito(request)
    carrito.items.all().delete()
    messages.success(request, 'Carrito vaciado.')
    return redirect('view_cart')

def orders(request):
    pedidos = Pedido.objects.select_related('id_usuario').prefetch_related(
        'comprobante__id_metodo_pago',
        'detalles__id_producto',
        'detalles__id_producto_color__id_color_general'
    ).order_by('-fecha_pedido')
    return render(request, 'orders.html', {'pedidos': pedidos})


def confirm_payment(request, comprobante_id):
    if request.method == 'POST':
        comprobante = get_object_or_404(ComprobantePago, id=comprobante_id)
        comprobante.confirmado = True
        comprobante.fecha_confirmacion = timezone.now()
        comprobante.save()

        pedido = comprobante.id_pedido
        pedido.estado = 'Confirmado'
        pedido.save()

        messages.success(request, f'Pago del Pedido #{pedido.id} confirmado exitosamente.')
    return redirect('orders')