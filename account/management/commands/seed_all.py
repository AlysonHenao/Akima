from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal

from account.models import User
from account.views import hash_password
from product.models import Product, ColorProduct, GeneralColor
from production.models import Supply, SupplyColorProduct, EmployeeInventory, ProductionTask
from order.models import (
    Order, OrderDetail, ShoppingCart, ItemCart,
    PaymentMethod, PaymentReceipt, FinancialMovement
)
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Seed completo de la base de datos Akima'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Eliminando datos...'))

        # PRODUCCIÓN
        ProductionTask.objects.all().delete()
        EmployeeInventory.objects.all().delete()
        SupplyColorProduct.objects.all().delete()
        Supply.objects.all().delete()

        # PEDIDOS / PAGOS / MOVIMIENTOS
        PaymentReceipt.objects.all().delete()
        FinancialMovement.objects.all().delete()
        OrderDetail.objects.all().delete()
        Order.objects.all().delete()
        ItemCart.objects.all().delete()
        ShoppingCart.objects.all().delete()
        PaymentMethod.objects.all().delete()

        # PRODUCTOS
        ColorProduct.objects.all().delete()
        Product.objects.all().delete()
        GeneralColor.objects.all().delete()

        # USUARIOS
        User.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('✔ Base limpia'))

        # USUARIOS
        admin = User.objects.create(
            first_name='Admin',
            last_name='Akima',
            email='admin@akima.com',
            password=hash_password('123456'),
            role='administrador',
            phone='3000000000',
            address='Oficina',
            city='Medellín'
        )

        empleada = User.objects.create(
            first_name='Luisa',
            last_name='Tejedora',
            email='empleada@akima.com',
            password=hash_password('123456'),
            role='empleada',
            phone='3001111111',
            address='Casa',
            city='Medellín'
        )

        cliente = User.objects.create(
            first_name='Ana',
            last_name='Cliente',
            email='cliente@akima.com',
            password=hash_password('123456'),
            role='cliente',
            phone='3002222222',
            address='Casa',
            city='Medellín'
        )

        self.stdout.write(self.style.SUCCESS('✔ Usuarios creados'))

        # PRODUCTOS 
        call_command('seed_products')
        self.stdout.write(self.style.SUCCESS('✔ Productos creados'))

        # SUPPLIES
        hilo = Supply.objects.create(
            type_supply='Hilo',
            brand='CottonSoft',
            reference='H001',
            quantity=1000,
            price=5000
        )

        boton = Supply.objects.create(
            type_supply='Botón',
            brand='Basic',
            reference='B001',
            quantity=500,
            price=500
        )

        self.stdout.write(self.style.SUCCESS('✔ Insumos creados'))

        # RELACION PRODUCTO-INSUMOS
        color_products = ColorProduct.objects.all()

        for cp in color_products:
            SupplyColorProduct.objects.create(
                color_product=cp,
                supply=hilo,
                required_quantity=Decimal('2.5')
            )

            SupplyColorProduct.objects.create(
                color_product=cp,
                supply=boton,
                required_quantity=Decimal('1')
            )

        self.stdout.write(self.style.SUCCESS('✔ Relación insumos-productos creada'))

        # INVENTARIO EMPLEADA
        EmployeeInventory.objects.create(
            employee=empleada,
            supply=hilo,
            available_quantity=Decimal('100')
        )

        EmployeeInventory.objects.create(
            employee=empleada,
            supply=boton,
            available_quantity=Decimal('50')
        )

        self.stdout.write(self.style.SUCCESS('✔ Inventario creado'))

        # MÉTODOS DE PAGO
        nequi = PaymentMethod.objects.create(
            name='Nequi',
            instructions='Realiza el pago al número 3001234567 y sube el comprobante en la plataforma.',
            active=True
        )

        daviplata = PaymentMethod.objects.create(
            name='Daviplata',
            instructions='Realiza el pago al número 3001234567 y sube el comprobante en la plataforma.',
            active=True
        )

        transferencia = PaymentMethod.objects.create(
            name='Transferencia Bancaria',
            instructions='Cuenta Bancolombia 123-456789-00 a nombre de Akima. Luego sube el comprobante.',
            active=True
        )

        self.stdout.write(self.style.SUCCESS('✔ Métodos de pago creados'))

        # ORDEN + DETALLE
        product = Product.objects.first()
        color_product = ColorProduct.objects.filter(product=product).first()

        order = Order.objects.create(
            user=cliente,
            subtotal=product.price,
            total=product.price,
            status='Confirmado'
        )

        OrderDetail.objects.create(
            order=order,
            product=product,
            color_product=color_product,
            size='M',
            quantity=1,
            unit_price=product.price,
        )

        self.stdout.write(self.style.SUCCESS('✔ Pedido creado'))

        # TAREA DE PRODUCCIÓN
        ProductionTask.objects.create(
            employee=empleada,
            product=color_product,
            order_detail=order.details.first(),
            status='Pendiente'
        )

        self.stdout.write(self.style.SUCCESS('✔ Tarea creada'))

        self.stdout.write(self.style.SUCCESS('🔥 SEED COMPLETO EJECUTADO'))