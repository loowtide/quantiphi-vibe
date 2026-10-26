from django.contrib import admin
from .models import Notification, PingCooldown


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'sender__username', 'message']


@admin.register(PingCooldown)
class PingCooldownAdmin(admin.ModelAdmin):
    list_display = ['sender', 'task', 'last_pinged_at']
    search_fields = ['sender__username', 'task__title']
