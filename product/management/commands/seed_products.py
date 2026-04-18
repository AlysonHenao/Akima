from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files.base import ContentFile
from product.models import GeneralColor, Product, ColorProduct, ProductImage
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont
import io
import os


class Command(BaseCommand):
    help = 'Seed the database with realistic crochet products'

    def generate_product_image(self, product_name, color_name):
        """Generate a simple product image with PIL"""
        width, height = 400, 500
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        color_map = {
            'Negro': '#1a1a1a',
            'Blanco': '#ffffff',
            'Rojo': '#ff0000',
            'Rosa': '#ffb6d9',
            'Naranja': '#ff8c00',
            'Amarillo': '#ffff00',
            'Verde': '#00aa00',
            'Azul': '#0066ff',
            'Turquesa': '#40e0d0',
            'Morado': '#9933ff',
            'Marrón': '#8b4513',
            'Gris': '#808080',
            'Beige': '#f5e6d3',
            'Metalizado': '#c0c0c0',
            'Multicolor': '#ff69b4',
        }

        color_hex = color_map.get(color_name, '#cccccc')
        
        for i in range(0, width, 20):
            for j in range(0, height, 20):
                draw.ellipse(
                    [i+2, j+2, i+18, j+18],
                    fill=color_hex,
                    outline='#999999'
                )

        text_y = height - 80
        draw.text(
            (width // 2, text_y),
            product_name[:20],
            fill='#333333',
            anchor='mm'
        )
        draw.text(
            (width // 2, text_y + 40),
            color_name,
            fill='#666666',
            anchor='mm'
        )

        img_io = io.BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)
        
        return img_io

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting database seed...'))

        colors_data = [
            'Negro',
            'Blanco',
            'Rojo',
            'Rosa',
            'Naranja',
            'Amarillo',
            'Verde',
            'Azul',
            'Turquesa',
            'Morado',
            'Marrón',
            'Gris',
            'Beige',
            'Metalizado',
            'Multicolor',
        ]

        colors = {}
        for color_name in colors_data:
            color, created = GeneralColor.objects.get_or_create(name=color_name)
            colors[color_name] = color
            if created:
                self.stdout.write(f'Created color: {color_name}')

        products_data = [
            {
                'category': 'Bikini',
                'name': 'Bikini Crochet Clásico',
                'description': 'Bikini de crochet 100% algodón tejido a mano. Perfecto para la playa con diseño en punto alto tradicional. Tejido con amor y dedicación.',
                'price': Decimal('185000.00'),
                'stock': 15,
                'manufacturing_time': 8,
                'active': True,
                'colors': ['Blanco', 'Negro', 'Naranja', 'Turquesa']
            },
            {
                'category': 'Bikini',
                'name': 'Bikini Crochet Flecos',
                'description': 'Bikini de crochet con flecos en los bordes. Diseño moderno y cómodo, ideal para disfrutar del verano. Hecho con hilo de algodón premium.',
                'price': Decimal('210000.00'),
                'stock': 12,
                'manufacturing_time': 10,
                'active': True,
                'colors': ['Blanco', 'Rosa', 'Amarillo']
            },
            {
                'category': 'Top',
                'name': 'Top Crochet Triángulo',
                'description': 'Top de crochet con diseño triangular. Versátil para playa o como prenda casual. Puede combinarse con faldas o shorts.',
                'price': Decimal('155000.00'),
                'stock': 20,
                'manufacturing_time': 6,
                'active': True,
                'colors': ['Negro', 'Blanco', 'Naranja', 'Rosa', 'Azul']
            },
            {
                'category': 'Top',
                'name': 'Top Crochet Halter',
                'description': 'Top estilo halter tejido en crochet. Ideal para días calurosos con excelente comodidad y estilo.',
                'price': Decimal('168000.00'),
                'stock': 18,
                'manufacturing_time': 7,
                'active': True,
                'colors': ['Blanco', 'Rosa', 'Beige']
            },
            {
                'category': 'Falda',
                'name': 'Falda Crochet Playa',
                'description': 'Falda de crochet perfecta para la playa. Con vuelo cómodo y diseño aireado. Hecha 100% a mano.',
                'price': Decimal('195000.00'),
                'stock': 14,
                'manufacturing_time': 9,
                'active': True,
                'colors': ['Blanco', 'Negro', 'Amarillo', 'Multicolor']
            },
            {
                'category': 'Falda',
                'name': 'Falda Crochet Larga',
                'description': 'Falda larga de crochet con patrón elegante. Perfecta para eventos o uso casual. Tejida con precisión artesanal.',
                'price': Decimal('265000.00'),
                'stock': 8,
                'manufacturing_time': 12,
                'active': True,
                'colors': ['Negro', 'Blanco', 'Beige']
            },
            {
                'category': 'Vestido',
                'name': 'Vestido Crochet Clásico',
                'description': 'Vestido de crochet elegante y cómodo. Diseño clásico que se adapta a cualquier ocasión. Perfecto para el verano.',
                'price': Decimal('315000.00'),
                'stock': 10,
                'manufacturing_time': 14,
                'active': True,
                'colors': ['Blanco', 'Negro', 'Rosa']
            },
            {
                'category': 'Vestido',
                'name': 'Vestido Crochet Mini',
                'description': 'Vestido corto de crochet con dibujos geométricos. Ideal para la playa o eventos casuales. Hecho con hilo de alta calidad.',
                'price': Decimal('225000.00'),
                'stock': 13,
                'manufacturing_time': 11,
                'active': True,
                'colors': ['Blanco', 'Naranja', 'Amarillo', 'Verde']
            },
            {
                'category': 'Short',
                'name': 'Short Crochet Playa',
                'description': 'Short de crochet ideal para la playa. Cómodo y estiloso, perfecto para combinaciones de verano.',
                'price': Decimal('145000.00'),
                'stock': 22,
                'manufacturing_time': 5,
                'active': True,
                'colors': ['Blanco', 'Negro', 'Azul', 'Rosa']
            },
            {
                'category': 'Set',
                'name': 'Set Crochet Playero',
                'description': 'Set completo de crochet para la playa. Incluye top y short a juego. Diseño coordinado y elegante.',
                'price': Decimal('350000.00'),
                'stock': 9,
                'manufacturing_time': 16,
                'active': True,
                'colors': ['Blanco', 'Negro', 'Rosa']
            },
            {
                'category': 'Accesorio',
                'name': 'Pulsera Crochet',
                'description': 'Pulsera tejida en crochet. Accesorio perfecto para complementar cualquier look de verano.',
                'price': Decimal('49000.00'),
                'stock': 50,
                'manufacturing_time': 1,
                'active': True,
                'colors': ['Multicolor', 'Negro', 'Blanco', 'Rosa', 'Azul']
            },
            {
                'category': 'Accesorio',
                'name': 'Collar Crochet',
                'description': 'Collar hecho 100% en crochet. Diseño único y elegante para cualquier ocasión.',
                'price': Decimal('73000.00'),
                'stock': 35,
                'manufacturing_time': 2,
                'active': True,
                'colors': ['Multicolor', 'Beige', 'Negro']
            },
            {
                'category': 'Accesorio',
                'name': 'Gorro Crochet',
                'description': 'Gorro tejido en crochet. Perfecto para el verano con diseño fresco y transpirable.',
                'price': Decimal('89000.00'),
                'stock': 25,
                'manufacturing_time': 3,
                'active': True,
                'colors': ['Blanco', 'Negro', 'Naranja', 'Rosa', 'Azul']
            },
            {
                'category': 'Pantalón',
                'name': 'Pantalón Crochet Casual',
                'description': 'Pantalón de crochet con diseño aireado. Perfecto para días calurosos manteniendo el estilo.',
                'price': Decimal('235000.00'),
                'stock': 11,
                'manufacturing_time': 10,
                'active': True,
                'colors': ['Blanco', 'Beige', 'Negro']
            },
            {
                'category': 'Camisa',
                'name': 'Camisa Crochet Open-Back',
                'description': 'Camisa de crochet con espalda abierta. Diseño moderno y fresco para looks casuales de verano.',
                'price': Decimal('250000.00'),
                'stock': 10,
                'manufacturing_time': 11,
                'active': True,
                'colors': ['Blanco', 'Negro', 'Beige']
            },
            {
                'category': 'Otro',
                'name': 'Bolsa Crochet Playera',
                'description': 'Bolsa tejida en crochet perfecta para llevar tus cosas a la playa. Bolsillo y asa cómodos.',
                'price': Decimal('142000.00'),
                'stock': 18,
                'manufacturing_time': 6,
                'active': True,
                'colors': ['Blanco', 'Negro', 'Multicolor']
            },
        ]

        # Create products and assign colors
        for product_data in products_data:
            colors_list = product_data.pop('colors')
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created product: {product.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Product already exists: {product.name}')
                )

            for color_name in colors_list:
                color_product, color_created = ColorProduct.objects.get_or_create(
                    product=product,
                    general_color=colors[color_name],
                    defaults={'available': True}
                )
                if color_created:
                    self.stdout.write(f'  ├─ Added color: {color_name}')

            for color_name in colors_list:
                img_io = self.generate_product_image(product.name, color_name)
                
                image_filename = f'{product.id}_{color_name.lower()}.png'
                
                # Delete existing image if it exists
                ProductImage.objects.filter(
                    product=product,
                    url_image=image_filename
                ).delete()
                
                # Create new product image
                product_image = ProductImage(product=product)
                product_image.url_image.save(
                    image_filename,
                    ContentFile(img_io.getvalue()),
                    save=True
                )
                self.stdout.write(f'  ├─ Added image: {color_name}')

        self.stdout.write(
            self.style.SUCCESS('✓ Database seeding completed successfully!')
        )
