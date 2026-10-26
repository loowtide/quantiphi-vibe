from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('<int:project_id>/create/', views.task_create, name='create'),
    path('<int:project_id>/<int:pk>/', views.task_detail, name='detail'),
    path('<int:project_id>/<int:pk>/edit/', views.task_edit, name='edit'),
    path('<int:project_id>/<int:pk>/delete/', views.task_delete, name='delete'),
    path('<int:project_id>/<int:pk>/move/', views.task_move, name='move'),
    path('<int:project_id>/workload/', views.workload_partial, name='workload'),
]
