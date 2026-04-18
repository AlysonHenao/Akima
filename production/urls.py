from django.urls import path
from . import views

urlpatterns = [
    path('administrator/production/', views.display_manufacturing_process, name='production_panel'),
    path('administrator/production/assign/', views.assign_products_to_employees, name='assign_task'),
    path('employee_panel/', views.view_assigned_products, name='employee_panel'),
    path('employee/', views.view_employee_information, name='employee'),
]
