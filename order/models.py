from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

from product.models import Product, ColorProduct
from account.models import User


class Order(models.Model):
    STATUS = [
        ('Pendiente confirmacion', 'Confirmación de pago pendiente'),
        ('Confirmado', 'Confirmado'),
        ('En producción', 'En producción'),
        ('Completado', 'Completado'),
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado'),
        ('Cancelado', 'Cancelado'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Customer',
        related_name='orders',
        null=True,
        blank=True,
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',
        verbose_name='Assigned Employee'
    )

    order_date = models.DateTimeField('Order Date', auto_now_add=True)
    subtotal = models.IntegerField('Subtotal', validators=[MinValueValidator(0)])
    discount = models.IntegerField('Discount', default=0, validators=[MinValueValidator(0)])
    total = models.IntegerField('Total', validators=[MinValueValidator(0)])
    status = models.CharField('Status', max_length=30, choices=STATUS, default='Pendiente confirmacion')
    customer_note = models.TextField('Customer Note', blank=True, null=True)

    class Meta:
        db_table = 'order'
        ordering = ['-order_date']

    def __str__(self):
        customer = f"{self.user.first_name} {self.user.last_name}" if self.user else 'Invitado'
        return f"Order #{self.id} - {customer} ({self.status})"

    @property
    def formatted_price(self):
        return f"${self.total:,.0f}".replace(',', '.')


class OrderDetail(models.Model):
    SIZE = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Order',
        related_name='details'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Product',
        related_name='order_details'
    )
    color_product = models.ForeignKey(
        ColorProduct,
        on_delete=models.PROTECT,
        verbose_name='Color',
        related_name='order_details'
    )
    size = models.CharField('Size', max_length=3, choices=SIZE)
    quantity = models.IntegerField('Quantity', validators=[MinValueValidator(1)])
    unit_price = models.IntegerField('Unit Price', validators=[MinValueValidator(0)])
    subtotal = models.IntegerField('Subtotal', validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'order_detail'

    @property
    def formatted_unit_price(self):
        return f"${self.unit_price:,.0f}".replace(',', '.')

    @property
    def formatted_subtotal(self):
        return f"${self.subtotal:,.0f}".replace(',', '.')

    def __str__(self):
        return f"Order #{self.order.id} - {self.product.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Customer',
        related_name='cart',
        null=True,
        blank=True
    )
    session_key = models.CharField('Session Key', max_length=40, null=True, blank=True)
    created_date = models.DateTimeField('Created At', auto_now_add=True)
    updated_date = models.DateTimeField('Updated At', auto_now=True)

    class Meta:
        db_table = 'shopping_cart'

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.first_name} {self.user.last_name}"
        return f"Cart (Session: {self.session_key})"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    @property
    def formatted_total(self):
        total = self.get_total()
        return f"${total:,.0f}".replace(',', '.')


class ItemCart(models.Model):
    SIZE = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    ]

    cart = models.ForeignKey(
        ShoppingCart,
        on_delete=models.CASCADE,
        verbose_name='Cart',
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Product',
        related_name='cart_items'
    )
    color_product = models.ForeignKey(
        ColorProduct,
        on_delete=models.CASCADE,
        verbose_name='Color',
        related_name='cart_items'
    )
    size = models.CharField('Size', max_length=3, choices=SIZE)
    quantity = models.IntegerField('Quantity', default=1, validators=[MinValueValidator(1)])
    unit_price = models.IntegerField('Unit Price', validators=[MinValueValidator(0)])
    addition_date = models.DateTimeField('Added At', auto_now_add=True)

    class Meta:
        db_table = 'cart_item'

    def __str__(self):
        return f"{self.product.name} ({self.color_product.general_color.name}, {self.size}) x{self.quantity}"

    def get_subtotal(self):
        return self.unit_price * self.quantity

    @property
    def formatted_unit_price(self):
        return f"${self.unit_price:,.0f}".replace(',', '.')

    @property
    def formatted_subtotal(self):
        subtotal = self.get_subtotal()
        return f"${subtotal:,.0f}".replace(',', '.')


class PaymentMethod(models.Model):
    name = models.CharField('Name', max_length=100, unique=True)
    instructions = models.TextField('Instructions')
    qr_image = models.ImageField('Payment QR', upload_to='payment_methods/', null=True, blank=True)
    active = models.BooleanField('Active', default=True)

    class Meta:
        db_table = 'payment_method'

    def __str__(self):
        return self.name


class PaymentReceipt(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        verbose_name='Order',
        related_name='receipts'
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        verbose_name='Payment Method',
        related_name='receipts'
    )
    receipt = models.ImageField('Payment Receipt', upload_to='receipts/', null=True, blank=True)
    amount = models.IntegerField('Amount', validators=[MinValueValidator(0)])
    upload_date = models.DateTimeField('Upload Date', auto_now_add=True)
    confirm = models.BooleanField('Confirmed', default=False)
    confirm_date = models.DateTimeField('Confirmation Date', blank=True, null=True)

    class Meta:
        db_table = 'payment_receipt'

    @property
    def formatted_amount(self):
        return f"${self.amount:,.0f}".replace(',', '.')

    def __str__(self):
        return f"Receipt Order #{self.order.id} - ${self.amount}"


class FinancialMovement(models.Model):
    TYPES = [
        ('Ingreso', 'Ingreso'),
        ('Egreso', 'Egreso'),
    ]

    CATEGORIES = [
        ('Venta', 'Venta'),
        ('Compra de insumos', 'Compra de insumos'),
        ('Pago a empleados', 'Pago a empleados'),
        ('Otro', 'Otro'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Orden',
        related_name='financial_movements'
    )
    user = models.ForeignKey(
        'account.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario',
        related_name='financial_movements'
    )
    category = models.CharField('Category', max_length=20, choices=CATEGORIES)
    type = models.CharField('Type', max_length=10, choices=TYPES)
    concept = models.CharField('Concept', max_length=255, default='')
    amount = models.IntegerField('Amount', validators=[MinValueValidator(0)])
    movement_date = models.DateTimeField('Date of Movement', auto_now_add=True)
    receipt = models.ImageField('Receipt', upload_to='financial_receipts/', null=True, blank=True)
    note = models.TextField('Note', blank=True, null=True)

    class Meta:
        db_table = 'financial_movement'

    @property
    def formatted_amount(self):
        return f"${self.amount:,.0f}".replace(',', '.')

    def __str__(self):
        return f"{self.type} - {self.category} - ${self.amount}"