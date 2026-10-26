from .models import Notification


def unread_notifications(request):
    """Context processor: inject unread notification count into every template."""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        recent_notifications = Notification.objects.filter(
            recipient=request.user
        ).select_related('sender', 'task')[:5]
        return {
            'unread_notification_count': unread_count,
            'recent_notifications': recent_notifications,
        }
    return {
        'unread_notification_count': 0,
        'recent_notifications': [],
    }
