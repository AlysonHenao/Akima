from django.urls import path
from . import views

urlpatterns = [
    path('administrator/production/', views.display_manufacturing_process, name='production_panel'),
    path('administrator/production/assign/', views.assign_products_to_employees, name='assign_task'),

    #  NUEVA RUTA (CONSULT MANUFACTURING INFO)
    path('administrator/production/consult/', views.consult_manufacturing_information, name='consult_manufacturing'),

    path('employee_panel/', views.view_assigned_products, name='employee_panel'),
    path('employee/', views.view_employee_information, name='employee'),

    path('employee/task/<int:task_id>/start/', views.start_task_supplies, name='start_task_supplies'),
    path('employee/task/<int:task_id>/finish/', views.finish_task_supplies, name='finish_task_supplies'),
    path('employee/task/<int:task_id>/add-supply/', views.add_supply_to_task, name='add_supply_to_task'),

    path('employee/inventory/', views.view_inventory, name='view_inventory'),
    path('employee/inventory/add/', views.add_supply_to_inventory, name='add_supply_to_inventory'),
    path('employee/inventory/create-supply/', views.create_supply, name='create_supply'),
]