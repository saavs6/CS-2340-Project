from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('new/', views.new_conversation, name='new_conversation'),
    path('start/<int:user_id>/', views.start_conversation_with_user, name='start_conversation_with_user'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('<int:conversation_id>/mark-read/', views.mark_conversation_read, name='mark_conversation_read'),
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
]
