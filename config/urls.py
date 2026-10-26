"""
URL configuration for kanban project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('notifications/', include('notifications.urls')),
    path('comments/', include('comments.urls')),
    path('', lambda request: redirect('projects:list'), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
