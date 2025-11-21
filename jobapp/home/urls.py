from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('admin-tools/', views.admin_dashboard, name='home.admin_dashboard'),
    path('admin-tools/export/', views.export_csv, name='home.export_csv'),
]