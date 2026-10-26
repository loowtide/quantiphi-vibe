from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('<int:project_id>/add/', views.add_comment, name='add'),
    path('<int:project_id>/<int:pk>/delete/', views.delete_comment, name='delete'),
]
