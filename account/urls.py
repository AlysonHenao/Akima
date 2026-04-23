from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register,     name='register'),
    path('login/',    views.login_view,   name='login'),
    path('logout/',   views.logout_view,  name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/users/<int:user_id>/role/', views.update_user_role, name='update_user_role'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('update-role/<int:user_id>/', views.update_user_role, name='update_user_role'),
]