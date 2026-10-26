from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='list'),
    path('create/', views.project_create, name='create'),
    path('<int:pk>/board/', views.project_board, name='board'),
    path('<int:pk>/settings/', views.project_settings, name='settings'),
    path('<int:pk>/delete/', views.project_delete, name='delete'),
    path('<int:pk>/members/<int:user_id>/remove/', views.remove_member, name='remove_member'),
]
