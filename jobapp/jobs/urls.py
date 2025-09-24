from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Public job views (for job seekers)
    path('', views.job_list, name='list'),
    path('<int:pk>/', views.job_detail, name='detail'),
    path('<int:pk>/apply/', views.job_apply, name='apply'),
    path('applications/', views.my_applications, name='my_applications'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('applications/<int:pk>/withdraw/', views.application_withdraw, name='application_withdraw'),
    
    # Recruiter views
    path('post/', views.job_create, name='create'),
    path('<int:pk>/edit/', views.job_edit, name='edit'),
    path('my-jobs/', views.recruiter_jobs, name='recruiter_jobs'),
]