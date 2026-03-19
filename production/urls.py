from django.urls import path
from . import views

urlpatterns = [
    # Rf-34: Display manufacturing process
    path('administrator/production/', views.display_manufacturing_process, name='production_panel'),

    # Rf-25: Assign products to employees (+ Rf-18 notify embebido)
    path('administrator/production/assign/', views.assign_products_to_employees, name='assign_task'),

    # Rf-17: View assigned products
    path('employee_panel/', views.view_assigned_products, name='employee_panel'),

    # Rf-31: View employee information
    path('employee/', views.view_employee_information, name='employee'),
]
