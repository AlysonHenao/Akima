from django.db import models


class User(models.Model):
    ROLES = [
        ('cliente', 'Cliente'),
        ('empleada', 'Empleada'),
        ('administrador', 'Administrador'),
    ]

    first_name = models.CharField('First Name', max_length=100)
    last_name = models.CharField('Last Name', max_length=100)
    email = models.EmailField('Email', max_length=100, unique=True)
    password = models.CharField('Password', max_length=128)
    role = models.CharField('Role', max_length=20, choices=ROLES)
    phone = models.CharField('Phone', max_length=20)
    address = models.CharField('Address', max_length=255)
    city = models.CharField('City', max_length=100)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"