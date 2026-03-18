from django.contrib import admin
from .models import Supply, SupplyColorProduct, EmployeeInventory, ProductionTask, SupplyTask

admin.site.register(Supply)
admin.site.register(SupplyColorProduct)
admin.site.register(EmployeeInventory)
admin.site.register(ProductionTask)
admin.site.register(SupplyTask)