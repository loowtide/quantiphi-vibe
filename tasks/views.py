from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.core.exceptions import PermissionDenied
import json

from projects.models import Project
from .models import Task
from .forms import TaskForm


def get_project_member_or_403(project_id, user):
    project = get_object_or_404(Project, pk=project_id)
    if not project.is_member(user):
        raise PermissionDenied
    return project


@login_required
def task_create(request, project_id):
    project = get_project_member_or_403(project_id, request.user)
    if request.method == 'POST':
        form = TaskForm(project, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            # Set position to end of column
            last_pos = Task.objects.filter(project=project, status=task.status).count()
            task.position = last_pos
            task.save()

            if request.htmx:
                # Return updated column partial
                tasks = project.tasks.filter(status=task.status).order_by('position')
                return render(request, 'tasks/partials/column_tasks.html', {
                    'tasks': tasks,
                    'status': task.status,
                    'project': project,
                    'count': tasks.count(),
                })
            messages.success(request, f'Task "{task.title}" created!')
            return redirect('projects:board', pk=project.pk)
        else:
            if request.htmx:
                return render(request, 'tasks/partials/task_form.html', {
                    'form': form, 'project': project
                }, status=422)
    else:
        status = request.GET.get('status', 'todo')
        form = TaskForm(project, initial={'status': status})

    if request.htmx:
        return render(request, 'tasks/partials/task_form.html', {
            'form': form, 'project': project
        })
    return render(request, 'tasks/task_form_page.html', {'form': form, 'project': project})


@login_required
def task_detail(request, project_id, pk):
    project = get_project_member_or_403(project_id, request.user)
    task = get_object_or_404(Task, pk=pk, project=project)
    if request.htmx:
        return render(request, 'tasks/partials/task_detail.html', {
            'task': task, 'project': project
        })
    return render(request, 'tasks/task_detail.html', {'task': task, 'project': project})


@login_required
def task_edit(request, project_id, pk):
    project = get_project_member_or_403(project_id, request.user)
    task = get_object_or_404(Task, pk=pk, project=project)

    if request.method == 'POST':
        form = TaskForm(project, request.POST, instance=task)
        if form.is_valid():
            old_status = task.status
            task = form.save()

            if request.htmx:
                # Re-render both old and new column if status changed
                return render(request, 'tasks/partials/task_card.html', {
                    'task': task, 'project': project
                })
            messages.success(request, 'Task updated.')
            return redirect('projects:board', pk=project.pk)
        else:
            if request.htmx:
                return render(request, 'tasks/partials/task_edit_form.html', {
                    'form': form, 'task': task, 'project': project
                }, status=422)
    else:
        form = TaskForm(project, instance=task)

    if request.htmx:
        return render(request, 'tasks/partials/task_edit_form.html', {
            'form': form, 'task': task, 'project': project
        })
    return render(request, 'tasks/task_form_page.html', {
        'form': form, 'task': task, 'project': project, 'editing': True
    })


@login_required
@require_POST
def task_delete(request, project_id, pk):
    project = get_project_member_or_403(project_id, request.user)
    task = get_object_or_404(Task, pk=pk, project=project)
    status = task.status
    task.delete()

    if request.htmx:
        tasks = project.tasks.filter(status=status).order_by('position')
        return render(request, 'tasks/partials/column_tasks.html', {
            'tasks': tasks,
            'status': status,
            'project': project,
            'count': tasks.count(),
        })
    messages.success(request, 'Task deleted.')
    return redirect('projects:board', pk=project.pk)


@login_required
@require_POST
def task_move(request, project_id, pk):
    """HTMX endpoint — update task status and position via drag-and-drop."""
    project = get_project_member_or_403(project_id, request.user)
    task = get_object_or_404(Task, pk=pk, project=project)

    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        new_position = int(data.get('position', 0))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid data'}, status=400)

    valid_statuses = ['todo', 'in_progress', 'done']
    if new_status not in valid_statuses:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    old_status = task.status
    task.status = new_status
    task.position = new_position
    task.save()

    # Reorder tasks in the target column
    tasks_in_column = Task.objects.filter(
        project=project, status=new_status
    ).exclude(pk=task.pk).order_by('position')
    for i, t in enumerate(tasks_in_column):
        if i >= new_position:
            t.position = i + 1
            t.save(update_fields=['position'])

    return JsonResponse({
        'status': 'ok',
        'task_id': task.pk,
        'new_status': new_status,
        'todo_count': project.tasks.filter(status='todo').count(),
        'in_progress_count': project.tasks.filter(status='in_progress').count(),
        'done_count': project.tasks.filter(status='done').count(),
    })


@login_required
def workload_partial(request, project_id):
    """HTMX partial — refresh workload panel."""
    project = get_project_member_or_403(project_id, request.user)
    members = project.members.all().select_related('profile')
    member_workload = []
    for member in members:
        active_count = Task.objects.filter(
            project=project, assigned_to=member, status='in_progress'
        ).count()
        member_workload.append({
            'user': member,
            'active_count': active_count,
            'overloaded': active_count > 5,
        })
    return render(request, 'tasks/partials/workload.html', {
        'member_workload': member_workload, 'project': project
    })
