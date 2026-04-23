from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

from product.models import GeneralColor, ColorProduct
from account.models import User


class Supply(models.Model):
    TYPES = [
        ('Hilo', 'Hilo'),
        ('Botón', 'Botón'),
        ('Argolla', 'Argolla'),
        ('Otro', 'Otro'),
    ]

    general_color = models.ForeignKey(
        GeneralColor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='General Color',
        related_name='supplies'
    )
    type_supply = models.CharField('Type', max_length=20, choices=TYPES)
    brand = models.CharField('Brand', max_length=100)
    reference = models.CharField('Reference', max_length=100)
    hex_code = models.CharField('HEX Code', max_length=7, blank=True, null=True, help_text='Format: #RRGGBB')
    quantity = models.DecimalField('Quantity', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    price = models.DecimalField('Price', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])

    class Meta:
        db_table = 'supply'

    def __str__(self):
        return f"{self.type_supply} - {self.brand} {self.reference}"


class SupplyColorProduct(models.Model):
    color_product = models.ForeignKey(
        ColorProduct,
        on_delete=models.CASCADE,
        verbose_name='Product Color',
        related_name='required_supplies'
    )
    supply = models.ForeignKey(
        Supply,
        on_delete=models.PROTECT,
        verbose_name='Supply',
        related_name='used_in_products'
    )
    required_quantity = models.DecimalField('Required Quantity', max_digits=10, decimal_places=3, validators=[MinValueValidator(Decimal('0.001'))])

    class Meta:
        db_table = 'supply_color_product'

    def __str__(self):
        return f"{self.color_product} - {self.supply} ({self.required_quantity})"


class EmployeeInventory(models.Model):
    employee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Employee',
        related_name='inventory'
    )
    supply = models.ForeignKey(
        Supply,
        on_delete=models.PROTECT,
        verbose_name='Supply',
        related_name='employee_inventory'
    )
    available_quantity = models.DecimalField(
        'Available Quantity',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    last_update = models.DateTimeField('Last Update', auto_now=True)

    class Meta:
        db_table = 'employee_inventory'

    def __str__(self):
        return f"{self.employee} - {self.supply} ({self.available_quantity})"


class ProductionTask(models.Model):
    STATUS = [
        ('Pendiente', 'Pendiente'),
        ('En progreso', 'En progreso'),
        ('Completada', 'Completada'),
        ('Cancelada', 'Cancelada'),
    ]

    order_detail = models.ForeignKey(
        'order.OrderDetail',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Order Detail',
        related_name='tasks'
    )

    employee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Employee',
        related_name='tasks'
    )

    product = models.ForeignKey(
        ColorProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Product',
        related_name='tasks'
    )

    assignment_date = models.DateTimeField(
        'Fecha de asignación',
        auto_now_add=True,
        null=True,
        blank=True
    )

    initial_date = models.DateTimeField('Fecha inicio', null=True, blank=True)
    final_date = models.DateTimeField('Fecha fin', null=True, blank=True)

    status = models.CharField('Estado', max_length=20, choices=STATUS, default='Pendiente')
    specification = models.TextField('Especificación', blank=True, null=True)

    class Meta:
        db_table = 'production_task'

    def __str__(self):
        return f"Tarea #{self.id} - {self.employee} ({self.status})"


class SupplyTask(models.Model):
    task = models.ForeignKey(
        ProductionTask,
        on_delete=models.CASCADE,
        verbose_name='Task',
        related_name='supplies'
    )
    supply = models.ForeignKey(
        Supply,
        on_delete=models.PROTECT,
        verbose_name='Supply',
        related_name='task_supplies'
    )
    initial_quantity = models.DecimalField('Initial Quantity', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    final_quantity = models.DecimalField('Final Quantity', max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])

    class Meta:
        db_table = 'supply_task'

    def __str__(self):
        return f"Tarea #{self.task.id} - {self.supply}"