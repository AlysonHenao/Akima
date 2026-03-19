from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=100, verbose_name='Last Name')),
                ('email', models.EmailField(max_length=100, unique=True, verbose_name='Email')),
                ('password', models.CharField(max_length=128, verbose_name='Password')),
                ('role', models.CharField(choices=[('cliente', 'Cliente'), ('empleada', 'Empleada'), ('administrador', 'Administrador')], max_length=20, verbose_name='Role')),
                ('phone', models.CharField(max_length=20, verbose_name='Phone')),
                ('address', models.CharField(max_length=255, verbose_name='Address')),
                ('city', models.CharField(max_length=100, verbose_name='City')),
            ],
            options={'db_table': 'user'},
        ),
    ]
