from django.urls import path

from . import views

urlpatterns = [
    #general urls
    path('upload', views.handle_file, name='file_upload'),
    path('download', views.download_file, name='file_download'),
    
    #user urls
    path('user/chat', views.user_room, name='user_chat'),
    path('user/info', views.user_info, name='user_info'),
    path('user/history/select', views.user_history, name='user_history'),
    path('user/history/chat', views.user_history_chat, name='user_history'),
    
    
    ##volunteer urls
    path('volunteer/select', views.volunteer_select, name='volunteer_chat'),
    path('volunteer/chat', views.volunteer_room, name='volunteer_chat'),
    
    
    ##manager urls
    path('manager/history/select', views.manager_history_chat, name='manager_history')
]

