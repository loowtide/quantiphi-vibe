from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
import datetime

from tasks.models import Task
from projects.models import Project
from .models import Notification, PingCooldown


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'task', 'sender__profile')
    # Mark all as read when viewing the list
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
@require_POST
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    if request.htmx:
        return HttpResponse(status=204)
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.htmx:
        return render(request, 'notifications/partials/navbar_dropdown.html', {
            'recent_notifications': [],
            'unread_notification_count': 0,
        })
    return redirect('notifications:list')


@login_required
@require_POST
def ping_deadline(request, project_id, task_id):
    """Send a deadline ping to the assigned user of a task."""
    project = get_object_or_404(Project, pk=project_id)
    if not project.is_member(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    task = get_object_or_404(Task, pk=task_id, project=project)

    if not task.assigned_to:
        if request.htmx:
            return HttpResponse(
                '<span class="text-red-400 text-xs">No one is assigned to this task.</span>',
                status=400
            )
        return redirect('projects:board', pk=project_id)

    if task.assigned_to == request.user:
        if request.htmx:
            return HttpResponse(
                '<span class="text-yellow-400 text-xs">You cannot ping yourself.</span>',
                status=400
            )
        return redirect('projects:board', pk=project_id)

    # Check cooldown
    cooldown_seconds = getattr(settings, 'PING_COOLDOWN_SECONDS', 3600)
    cooldown_threshold = timezone.now() - datetime.timedelta(seconds=cooldown_seconds)
    cooldown, created = PingCooldown.objects.get_or_create(
        sender=request.user, task=task
    )

    if not created and cooldown.last_pinged_at > cooldown_threshold:
        remaining = int((cooldown.last_pinged_at - cooldown_threshold).total_seconds() / 60)
        if request.htmx:
            return HttpResponse(
                f'<span class="text-yellow-400 text-xs">⏳ Wait {remaining}m before pinging again.</span>',
                status=429
            )
        return redirect('projects:board', pk=project_id)

    # Update cooldown timestamp
    PingCooldown.objects.filter(pk=cooldown.pk).update(last_pinged_at=timezone.now())

    # Create notification
    due_str = task.due_date.strftime('%b %d') if task.due_date else 'soon'
    message = f'🔔 {request.user.get_full_name() or request.user.username} is reminding you about "{task.title}" — due {due_str}.'
    Notification.objects.create(
        recipient=task.assigned_to,
        sender=request.user,
        task=task,
        message=message,
        notification_type='ping',
    )

    if request.htmx:
        return HttpResponse(
            '<span class="text-green-400 text-xs">✓ Ping sent!</span>'
        )
    return redirect('projects:board', pk=project_id)
