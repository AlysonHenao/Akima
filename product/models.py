from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


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
    manufacturing_guide = models.FileField(upload_to='guides/manufacturing/', blank=True, null=True)
    size_guide = models.ImageField(upload_to='guides/sizes/', blank=True, null=True)

    class Meta:
        db_table = 'product'

    def __str__(self):
        return f"{self.name} ({self.category})"

    @property
    def formatted_price(self):
        """Format price in Colombian format (185.000,00)"""
        return f"${self.price:,.0f}".replace(',', '.')


class ColorProduct(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Product',
        related_name='colors'
    )
    general_color = models.ForeignKey(
        GeneralColor,
        on_delete=models.PROTECT,
        verbose_name='Color',
        related_name='product_colors'
    )
    available = models.BooleanField('Available', default=True)

    class Meta:
        db_table = 'product_color'

    def __str__(self):
        return f"{self.product.name} - {self.general_color.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Product',
        related_name='images'
    )
    url_image = models.ImageField('Image', upload_to='products/')

    class Meta:
        db_table = 'product_image'

    def __str__(self):
        return f"Image of {self.product.name}"


class SetProduct(models.Model):
    set_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Set Product',
        related_name='set_components',
        limit_choices_to={'category': 'Set'}
    )
    individual_product = models.ForeignKey(
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
        return f"{self.set_product.name} → {self.individual_product.name} (x{self.quantity})"