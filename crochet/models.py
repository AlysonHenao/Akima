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

    # Customization options
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
