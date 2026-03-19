from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateTimeField(auto_now_add=True, verbose_name='Order Date')),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Subtotal')),
                ('discount', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Discount')),
                ('total', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Total')),
                ('status', models.CharField(choices=[('Pendiente confirmacion', 'Confirmación de pago pendiente'), ('Confirmado', 'Confirmado'), ('En producción', 'En producción'), ('Completado', 'Completado'), ('Enviado', 'Enviado'), ('Entregado', 'Entregado'), ('Cancelado', 'Cancelado')], default='Pendiente confirmacion', max_length=30, verbose_name='Status')),
                ('customer_note', models.TextField(blank=True, null=True, verbose_name='Customer Note')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='account.user', verbose_name='Customer')),
            ],
            options={'db_table': 'order', 'ordering': ['-order_date']},
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')], max_length=3, verbose_name='Size')),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Quantity')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Unit Price')),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Subtotal')),
                ('color_product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_details', to='product.colorproduct', verbose_name='Color')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='order.order', verbose_name='Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_details', to='product.product', verbose_name='Product')),
            ],
            options={'db_table': 'order_detail'},
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=40, null=True, verbose_name='Session Key')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='account.user', verbose_name='Customer')),
            ],
            options={'db_table': 'shopping_cart'},
        ),
        migrations.CreateModel(
            name='ItemCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')], max_length=3, verbose_name='Size')),
                ('quantity', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Quantity')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Unit Price')),
                ('addition_date', models.DateTimeField(auto_now_add=True, verbose_name='Added At')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='order.shoppingcart', verbose_name='Cart')),
                ('color_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='product.colorproduct', verbose_name='Color')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='product.product', verbose_name='Product')),
            ],
            options={'db_table': 'cart_item'},
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('instructions', models.TextField(verbose_name='Instructions')),
                ('qr_image', models.ImageField(blank=True, null=True, upload_to='payment_methods/', verbose_name='Payment QR')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={'db_table': 'payment_method'},
        ),
        migrations.CreateModel(
            name='PaymentReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt', models.ImageField(blank=True, null=True, upload_to='receipts/', verbose_name='Payment Receipt')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Amount')),
                ('upload_date', models.DateTimeField(auto_now_add=True, verbose_name='Upload Date')),
                ('confirm', models.BooleanField(default=False, verbose_name='Confirmed')),
                ('confirm_date', models.DateTimeField(blank=True, null=True, verbose_name='Confirmation Date')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='receipts', to='order.order', verbose_name='Order')),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='receipts', to='order.paymentmethod', verbose_name='Payment Method')),
            ],
            options={'db_table': 'payment_receipt'},
        ),
        migrations.CreateModel(
            name='FinancialMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('Venta', 'Venta'), ('Compra de insumos', 'Compra de insumos'), ('Pago a empleados', 'Pago a empleados'), ('Otro', 'Otro')], max_length=20, verbose_name='Category')),
                ('type', models.CharField(choices=[('Ingreso', 'Ingreso'), ('Egreso', 'Egreso')], max_length=10, verbose_name='Type')),
                ('concept', models.CharField(default='', max_length=255, verbose_name='Concept')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Amount')),
                ('movement_date', models.DateTimeField(auto_now_add=True, verbose_name='Date of Movement')),
                ('receipt', models.ImageField(blank=True, null=True, upload_to='financial_receipts/', verbose_name='Receipt')),
                ('note', models.TextField(blank=True, null=True, verbose_name='Note')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='financial_movements', to='order.order', verbose_name='Orden')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='financial_movements', to='account.user', verbose_name='Usuario')),
            ],
            options={'db_table': 'financial_movement'},
        ),
    ]
