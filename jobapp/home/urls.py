from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('admin-tools/', views.admin_dashboard, name='home.admin_dashboard'),
    path('admin-tools/export/', views.export_csv, name='home.export_csv'),
    # Admin user management
    path('admin-tools/users/', views.admin_user_list, name='home.admin_user_list'),
    path('admin-tools/users/<int:user_id>/edit-role/', views.admin_edit_user_role, name='home.admin_edit_user_role'),
    path('admin-tools/users/<int:user_id>/toggle-active/', views.admin_toggle_user_active, name='home.admin_toggle_user_active'),
]