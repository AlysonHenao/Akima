from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import (
    Producto, ProductoColor, ProductoImagen, 
    ColorGeneral, SetProducto
)
from decimal import Decimal

def home(request):
    """Página principal - Muestra productos activos"""
    productos = Producto.objects.filter(activo=True)
    return render(request, 'home.html', {'productos': productos})


def owner(request):
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
            return redirect('owner')
            
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
    
    return render(request, 'owner.html', context)


def toggle_producto(request, producto_id):
    """Activar/desactivar producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    producto.activo = not producto.activo
    producto.save()
    
    estado = "activado" if producto.activo else "desactivado"
    messages.success(request, f'Producto "{producto.nombre}" {estado}.')
    
    return redirect('owner')


def employee(request):
    """Vista de empleados (por implementar)"""
    return render(request, 'employee.html')