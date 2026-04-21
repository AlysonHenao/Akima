from django.urls import path
from . import views

urlpatterns = [
    path('administrator/production/', views.display_manufacturing_process, name='production_panel'),
    path('administrator/production/assign/', views.assign_products_to_employees, name='assign_task'),
    path('employee_panel/', views.view_assigned_products, name='employee_panel'),
    path('employee/', views.view_employee_information, name='employee'),

    path('employee/task/<int:task_id>/start/', views.start_task_supplies, name='start_task_supplies'),
    path('employee/task/<int:task_id>/finish/', views.finish_task_supplies, name='finish_task_supplies'),
    path('employee/task/<int:task_id>/add-supply/', views.add_supply_to_task, name='add_supply_to_task'),
]