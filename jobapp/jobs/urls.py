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

    # Map views
    path('map/', views.job_map, name='map'),
    path('nearby/', views.jobs_nearby_api, name='nearby_api'),
    path('save-location/', views.save_job_location, name='save_location'),
    path('jobs-without-coords/', views.jobs_without_coordinates_api, name='jobs_without_coords'),

    # Recruiter views
    path('post/', views.job_create, name='create'),
    path('<int:pk>/edit/', views.job_edit, name='edit'),
    path('my-jobs/', views.recruiter_jobs, name='recruiter_jobs'),
    path('my-jobs/map/', views.recruiter_job_map, name='recruiter_job_map'),
    # Applicant recommendations
    path('recommendations/', views.recommendations_list, name='recommendations_list'),
    path('recommendations/<int:pk>/', views.recommendation_detail, name='recommendation_detail'),
]