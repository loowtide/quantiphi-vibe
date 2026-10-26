from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('ping', 'Deadline Ping'),
        ('assignment', 'Task Assignment'),
        ('mention', 'Mention'),
    ]

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_notifications'
    )
    task = models.ForeignKey(
        'tasks.Task', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications'
    )
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='ping')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:50]}"


class PingCooldown(models.Model):
    """Track when a user last pinged about a specific task to prevent spam."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ping_cooldowns')
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, related_name='ping_cooldowns')
    last_pinged_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'task')
