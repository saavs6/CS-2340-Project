from django.urls import path
from . import views

app_name = 'recruiters'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('jobs/', views.job_postings, name='job_postings'),
    path('candidates/', views.candidates, name='candidates'),
    path('candidates/<int:pk>/', views.candidate_detail, name='candidate_detail'),
    path('candidates/map/', views.applicant_map, name='applicant_map'),
    path('jobs/<int:job_id>/applications/', views.job_applications, name='job_applications'),
    path('jobs/<int:job_id>/kanban/', views.kanban_board, name='kanban_board'),
    path('applications/<int:application_id>/', views.application_detail, name='application_detail'),
    path('api/update-application-status/', views.update_application_status, name='update_application_status'),
    # Saved searches
    path('saved-searches/', views.saved_search_list, name='saved_search_list'),
    path('saved-searches/create/', views.saved_search_create, name='saved_search_create'),
    path('saved-searches/<int:pk>/edit/', views.saved_search_edit, name='saved_search_edit'),
    path('saved-searches/<int:pk>/delete/', views.saved_search_delete, name='saved_search_delete'),
    path('saved-searches/<int:pk>/', views.saved_search_detail, name='saved_search_detail'),
]
