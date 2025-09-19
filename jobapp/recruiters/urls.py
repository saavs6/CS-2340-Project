from django.urls import path
from . import views

app_name = 'recruiters'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('jobs/', views.job_postings, name='job_postings'),
    path('candidates/', views.candidates, name='candidates'),
]
