from django.urls import path

from . import views

urlpatterns = [
    path('user/chat', views.user_room, name='user_chat'),
    path('volunteer/select', views.volunteer_select, name='volunteer_chat'),
    path('volunteer/chat', views.volunteer_room, name='volunteer_chat')
]