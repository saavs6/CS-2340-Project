from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Public job views (for job seekers)
    path('', views.job_list, name='list'),
    path('<int:pk>/', views.job_detail, name='detail'),
    
    # Recruiter views
    path('post/', views.job_create, name='create'),
    path('<int:pk>/edit/', views.job_edit, name='edit'),
    path('my-jobs/', views.recruiter_jobs, name='recruiter_jobs'),
]