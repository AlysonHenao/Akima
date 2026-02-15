from django.db import models

class Product(models.Model):

    CATEGORY_CHOICES = [
        ('Shirt', 'shirt'),
        ('pant', 'Pant'),
        ('skirt', 'Skirt'),
    ]

    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Extra Extra Large'),
    ]

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    name = models.CharField(max_length=150)

    image = models.ImageField(upload_to='product/images/',
                              null=True,
                              blank=True)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(default=0)

    available_sizes = models.CharField(
        max_length=200,
        help_text="Comma-separated sizes (e.g., XS,S,M,L,XL)",
        default="S,M,L"
    )

    available_colors = models.CharField(
        max_length=200,
        help_text="Comma-separated colors (e.g., Red,Blue,Green)",
        default="White,Black,Blue"
    )

    production_time = models.PositiveIntegerField(
        help_text="Time in days required to produce the product"
    )

    is_active = models.BooleanField(default=True)

    size_guide = models.ImageField(
        upload_to='size_guides/',
        null=True,
        blank=True
    )

    manufacturing_guide = models.FileField(
        upload_to='manufacturing_guides/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    def get_available_sizes(self):
        return [size.strip() for size in self.available_sizes.split(',') if size.strip()]

    def get_available_colors(self):
        return [color.strip() for color in self.available_colors.split(',') if color.strip()]


class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.session_key}"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} ({self.size}, {self.color})"

    def get_subtotal(self):
        return self.product.price * self.quantity

    class Meta:
        unique_together = ['cart', 'product', 'size', 'color']
