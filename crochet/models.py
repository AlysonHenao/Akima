from django.db import models

class Product(models.Model):

    CATEGORY_CHOICES = [
        ('Shirt', 'shirt'),
        ('pant', 'Pant'),
        ('skirt', 'Skirt'),
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
