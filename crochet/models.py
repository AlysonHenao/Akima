from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal


class Usuario(models.Model):
    
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    email = models.EmailField('Email', max_length=100, unique=True)
    telefono = models.CharField('Teléfono', max_length=20)
    direccion = models.CharField('Dirección', max_length=255)
    ciudad = models.CharField('Ciudad', max_length=100)
    
    class Meta:
        db_table = 'usuario'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.email}"

class ColorGeneral(models.Model):
    """ Catálogo de colores base del sistema"""
    nombre = models.CharField('Nombre del Color', max_length=50, unique=True)
    
    class Meta:
        db_table = 'color_general'
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    """ Catálogo de productos """
    CATEGORIAS = [
        ('Bikini', 'Bikini'),
        ('Top', 'Top'),
        ('Falda', 'Falda'),
        ('Buzo', 'Buzo'),
        ('Vestido', 'Vestido'),
        ('Short', 'Short'),
        ('Set', 'Set'),
        ('Accesorio', 'Accesorio'),
        ('Pantalón', 'Pantalón'),
        ('Camisa', 'Camisa'),
        ('Otro', 'Otro'),
    ]
    
    categoria = models.CharField('Categoría', max_length=20, choices=CATEGORIAS)
    nombre = models.CharField('Nombre', max_length=150)
    descripcion = models.TextField('Descripción')
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    stock = models.IntegerField('Stock', default=0, validators=[MinValueValidator(0)])
    tiempo_fabricacion = models.IntegerField('Tiempo de Fabricación (horas)', validators=[MinValueValidator(0)])
    activo = models.BooleanField('Activo', default=True)
    guia_fabricacion = models.FileField(upload_to='guias/fabricacion/', blank=True, null=True)
    guia_tallas = models.ImageField(upload_to='guias/tallas/', blank=True, null=True)
    
    class Meta:
        db_table = 'producto'
    
    def __str__(self):
        return f"{self.nombre} ({self.categoria})"

class ProductoColor(models.Model):
    """ Variantes de color disponibles para cada producto """
    id_producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        verbose_name='Producto',
        related_name='colores'
    )
    id_color_general = models.ForeignKey(
        ColorGeneral, 
        on_delete=models.PROTECT, 
        verbose_name='Color',
        related_name='productos_color'
    )
    disponible = models.BooleanField('Disponible', default=True)
    
    class Meta:
        db_table = 'producto_color'
    
    def __str__(self):
        return f"{self.id_producto.nombre} - {self.id_color_general.nombre}"

class ProductoImagen(models.Model):
    """ Galería de imágenes de productos """
    id_producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        verbose_name='Producto',
        related_name='imagenes'
    )
    url_imagen = models.ImageField('Imagen', upload_to='productos/')
    
    class Meta:
        db_table = 'producto_imagen'
    
    def __str__(self):
        return f"Imagen de {self.id_producto.nombre}"

class SetProducto(models.Model):
    """ Define qué productos componen un set y su precio dentro del set """
    id_producto_set = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        verbose_name='Producto Set',
        related_name='componentes_set',
        limit_choices_to={'categoria': 'Set'}
    )
    id_producto_individual = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        verbose_name='Producto Individual',
        related_name='pertenece_a_sets'
    )
    cantidad = models.IntegerField('Cantidad', validators=[MinValueValidator(1)])
    precio_set = models.DecimalField('Precio en Set', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], help_text='Precio con descuento aplicado')
    
    class Meta:
        db_table = 'set_producto'
    
    def __str__(self):
        return f"{self.id_producto_set.nombre} → {self.id_producto_individual.nombre} (x{self.cantidad})"

class MetodoPago(models.Model):
    """ Métodos de pago configurados en el sistema """
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    instrucciones = models.TextField('Instrucciones')
    activo = models.BooleanField('Activo', default=True)
    
    class Meta:
        db_table = 'metodo_pago'
    
    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    """ Órdenes de compra realizadas por clientes"""
    ESTADOS = [
        ('Pendiente pago', 'Confirmación de pago pendiente'),
        ('Confirmado', 'Confirmado'),
        ('En producción', 'En producción'),
        ('Completado', 'Completado'),
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado'),
        ('Cancelado', 'Cancelado'),
    ]
    
    id_usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT, 
        verbose_name='Cliente',
        related_name='pedidos'
    )
    fecha_pedido = models.DateTimeField('Fecha de Pedido', auto_now_add=True)
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    descuento = models.DecimalField('Descuento', max_digits=10, decimal_places=2, blank=True, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    estado = models.CharField('Estado', max_length=30, choices=ESTADOS, default='Pendiente pago')
    nota_cliente = models.TextField('Nota del Cliente', blank=True, null=True)
    
    class Meta:
        db_table = 'pedido'
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.id_usuario.nombre} {self.id_usuario.apellido} ({self.estado})"

class PedidoDetalle(models.Model):
    """ Items específicos de cada pedido """
    id_pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE, 
        verbose_name='Pedido',
        related_name='detalles'
    )
    id_producto = models.ForeignKey(
        Producto, 
        on_delete=models.PROTECT, 
        verbose_name='Producto',
        related_name='detalles_pedido'
    )
    id_producto_color = models.ForeignKey(
        ProductoColor, 
        on_delete=models.PROTECT, 
        verbose_name='Color',
        related_name='detalles_pedido'
    )
    talla = models.CharField('Talla', max_length=10)
    cantidad = models.IntegerField('Cantidad', validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField('Precio Unitario', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    
    class Meta:
        db_table = 'pedido_detalle'
    
    def __str__(self):
        return f"Pedido #{self.id_pedido.id} - {self.id_producto.nombre} x{self.cantidad}"
    
    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)

class ComprobantePago(models.Model):
    """ Evidencias de pagos realizados por clientes """
    id_pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.PROTECT, 
        verbose_name='Pedido',
        related_name='comprobante'
    )
    id_metodo_pago = models.ForeignKey(
        MetodoPago, 
        on_delete=models.PROTECT, 
        verbose_name='Método de Pago',
        related_name='comprobantes'
    )
    archivo_url = models.CharField('URL del Archivo', max_length=500)
    monto = models.DecimalField('Monto', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    fecha_subida = models.DateTimeField('Fecha de Subida', auto_now_add=True)
    confirmado = models.BooleanField('Confirmado', default=False)
    fecha_confirmacion = models.DateTimeField('Fecha de Confirmación', blank=True, null=True)
    
    class Meta:
        db_table = 'comprobante_pago'
    
    def __str__(self):
        return f"Comprobante Pedido #{self.id_pedido.id} - ${self.monto}"

