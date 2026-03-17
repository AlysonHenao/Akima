from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal


class User(models.Model):
    first_name = models.CharField('First Name', max_length=100)
    last_name = models.CharField('Last Name', max_length=100)
    email = models.EmailField('Email', max_length=100, unique=True)
    password = models.CharField('Password', max_length=128)
    role = models.CharField('Role', max_length=128)
    phone = models.CharField('Phone', max_length=20)
    address = models.CharField('Address', max_length=255)
    city = models.CharField('City', max_length=100)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

class GeneralColor(models.Model):
    name = models.CharField('Color Name', max_length=50, unique=True)

    class Meta:
        db_table = 'general_color'

    def __str__(self):
        return self.name

class Product(models.Model):
    CATEGORIES = [
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

    category = models.CharField('Category', max_length=20, choices=CATEGORIES)
    name = models.CharField('Name', max_length=150)
    description = models.TextField('Description')
    price = models.DecimalField('Price', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    stock = models.IntegerField('Stock', default=0, validators=[MinValueValidator(0)])
    manufacturing_time = models.IntegerField('Manufacturing Time (hours)', validators=[MinValueValidator(0)])
    active = models.BooleanField('Active', default=True)
    manufacturing_guide = models.FileField(upload_to='guias/fabricacion/', blank=True, null=True)
    size_guide = models.ImageField(upload_to='guias/tallas/', blank=True, null=True)

    class Meta:
        db_table = 'product'

    def __str__(self):
        return f"{self.name} ({self.category})"

class ColorProduct(models.Model):
    id_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Product',
        related_name='colors'
    )
    id_general_color = models.ForeignKey(
        GeneralColor,
        on_delete=models.PROTECT,
        verbose_name='Color',
        related_name='product_colors'
    )
    available = models.BooleanField('Available', default=True)

    class Meta:
        db_table = 'product_color'

    def __str__(self):
        return f"{self.id_product.name} - {self.id_general_color.name}"

class ProductImage(models.Model):
    id_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Product',
        related_name='images'
    )
    url_image = models.ImageField('Image', upload_to='products/')

    class Meta:
        db_table = 'product_image'

    def __str__(self):
        return f"Image of {self.id_product.name}"

class SetProduct(models.Model):
    id_set_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Set Product',
        related_name='set_components',
        limit_choices_to={'category': 'Set'}
    )
    id_individual_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Individual Product',
        related_name='belongs_to_sets'
    )
    quantity = models.IntegerField('Quantity', validators=[MinValueValidator(1)])
    set_price = models.DecimalField('Set Price', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], help_text='Discounted price')

    class Meta:
        db_table = 'set_product'

    def __str__(self):
        return f"{self.id_set_product.name} → {self.id_individual_product.name} (x{self.quantity})"

class PaymentMethod(models.Model):
    name = models.CharField('Name', max_length=100, unique=True)
    instructions = models.TextField('Instructions')
    qr_image = models.ImageField('Payment QR', upload_to='payment_method/', null=True, blank=True)
    active = models.BooleanField('Active', default=True)

    class Meta:
        db_table = 'payment_method'

    def __str__(self):
        return self.name

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

    id_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Customer',
        related_name='orders',
        null=True,
        blank=True,
    )
    order_date = models.DateTimeField('Order Date', auto_now_add=True)
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    discount = models.DecimalField('Discount', max_digits=10, decimal_places=2, blank=True, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField('Status', max_length=30, choices=STATUS, default='Pendiente confirmacion')
    customer_note = models.TextField('Customer Note', blank=True, null=True)

    class Meta:
        db_table = 'order'
        ordering = ['-order_date']

    def __str__(self):
        if self.id_user:
            customer = f"{self.id_user.first_name} {self.id_user.last_name}"
        else:
            customer = 'Invitado'
        return f"Order #{self.id} - {customer} ({self.status})"

class OrderDetail(models.Model):
    SIZE = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    ]

    id_order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Order',
        related_name='details'
    )
    id_product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Product',
        related_name='order_details'
    )
    id_product_color = models.ForeignKey(
        ColorProduct,
        on_delete=models.PROTECT,
        verbose_name='Color',
        related_name='order_details'
    )
    size = models.CharField('Size', choices=SIZE)
    quantity = models.IntegerField('Quantity', validators=[MinValueValidator(1)])
    unit_price = models.DecimalField('Unit Price', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])

    class Meta:
        db_table = 'order_detail'

    def __str__(self):
        return f"Order #{self.id_order.id} - {self.id_product.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

class PaymentReceipt(models.Model):
    id_order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        verbose_name='Order',
        related_name='receipt'
    )
    id_payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        verbose_name='Payment Method',
        related_name='receipts'
    )
    receipt = models.ImageField('Payment Receipt', upload_to='receipts/', null=True, blank=True)
    amount = models.DecimalField('Amount', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    upload_date = models.DateTimeField('Upload Date', auto_now_add=True)
    confirm = models.BooleanField('Confirmed', default=False)
    confirm_date = models.DateTimeField('Confirmation Date', blank=True, null=True)

    class Meta:
        db_table = 'payment_receipt'

    def __str__(self):
        return f"Receipt Order #{self.id_order.id} - ${self.amount}"

class Supply(models.Model):
    TYPES = [
        ('Hilo', 'Hilo'),
        ('Botón', 'Botón'),
        ('Argolla', 'Argolla'),
        ('Otro', 'Otro'),
    ]

    type_supply = models.CharField('Type', choices=TYPES)
    brand = models.CharField('Brand', max_length=100)
    reference = models.CharField('Reference', max_length=100)
    color = models.CharField('Color', max_length=100)
    id_general_color = models.ForeignKey(
        GeneralColor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='General Color',
        related_name='supplies'
    )
    hex_code = models.CharField('HEX Code', max_length=7, blank=True, null=True, help_text='Format: #RRGGBB')
    quantity = models.DecimalField('Quantity', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    price = models.DecimalField('Price', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])

    class Meta:
        db_table = 'supply'

    def __str__(self):
        return f"{self.type_supply } - {self.brand} {self.reference} ({self.color})"

class ProductColorSupply(models.Model):
    id_product_color = models.ForeignKey(
        ColorProduct,
        on_delete=models.CASCADE,
        verbose_name='Product Color',
        related_name='required_supplies'
    )
    id_supply = models.ForeignKey(
        Supply,
        on_delete=models.PROTECT,
        verbose_name='Supply',
        related_name='used_in_products'
    )
    required_quantity = models.DecimalField('Required Quantity', max_digits=10, decimal_places=3, validators=[MinValueValidator(Decimal('0.001'))])

    class Meta:
        db_table = 'product_color_supply'

    def __str__(self):
        return f"{self.id_product_color} - {self.id_supply} ({self.required_quantity})"

class ShoppingCart(models.Model):
    id_user = models.ForeignKey(
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
        if self.id_user:
            return f"Cart of {self.id_user.first_name} {self.id_user.last_name}"
        return f"Cart (Session: {self.session_key})"

    def get_total(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        return total

class ItemCart(models.Model):
    SIZE = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    ]

    id_cart = models.ForeignKey(
        ShoppingCart,
        on_delete=models.CASCADE,
        verbose_name='Cart',
        related_name='items'
    )
    id_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Product',
        related_name='cart_items'
    )
    id_product_color = models.ForeignKey(
        ColorProduct,
        on_delete=models.CASCADE,
        verbose_name='Color',
        related_name='cart_items'
    )
    size = models.CharField('Size', max_length=3, choices=SIZE)
    quantity = models.IntegerField('Quantity', default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField('Unit Price', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    addition_date = models.DateTimeField('Added At', auto_now_add=True)

    class Meta:
        db_table = 'cart_item'

    def __str__(self):
        return f"{self.id_product.name} ({self.id_product_color.id_general_color.name}, {self.size}) x{self.quantity}"

    def get_subtotal(self):
        return self.unit_price * self.quantity
