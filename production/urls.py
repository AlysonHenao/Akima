from django.urls import path
from . import views

urlpatterns = [
    path('administrator/production/', views.production_panel, name='production_panel'),
    path('administrator/production/assign/', views.assign_task, name='assign_task'),
    path('employee_panel/', views.employee_panel, name='employee_panel'),
    path('employee/', views.employee, name='employee'),
]