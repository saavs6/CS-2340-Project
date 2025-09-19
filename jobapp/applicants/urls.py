from django.urls import path
from . import views

app_name = 'applicants'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('applications/', views.applications, name='applications'),
    path('search/', views.job_search, name='job_search'),
]
