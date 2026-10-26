from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from .models import Project, ProjectMember
from .forms import ProjectForm, AddMemberForm
from tasks.models import Task


def get_project_or_403(project_id, user):
    """Return project if user is a member, else raise 403."""
    from django.core.exceptions import PermissionDenied
    project = get_object_or_404(Project, pk=project_id)
    if not project.is_member(user):
        raise PermissionDenied
    return project


@login_required
def project_list(request):
    projects = Project.objects.filter(members=request.user) | Project.objects.filter(owner=request.user)
    projects = projects.distinct().order_by('-created_at')
    form = ProjectForm()
    return render(request, 'projects/list.html', {'projects': projects, 'form': form})


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            # Add owner as admin member
            ProjectMember.objects.create(project=project, user=request.user, role='admin')
            messages.success(request, f'Project "{project.name}" created!')
            return redirect('projects:board', pk=project.pk)
        messages.error(request, 'Please correct the errors below.')
    return redirect('projects:list')


@login_required
def project_board(request, pk):
    project = get_project_or_403(pk, request.user)
    priority_filter = request.GET.get('priority', '')

    tasks_qs = project.tasks.select_related('assigned_to', 'assigned_to__profile')
    if priority_filter:
        tasks_qs = tasks_qs.filter(priority=priority_filter)

    todo_tasks = tasks_qs.filter(status='todo').order_by('position')
    in_progress_tasks = tasks_qs.filter(status='in_progress').order_by('position')
    done_tasks = tasks_qs.filter(status='done').order_by('position')

    # Workload data
    members = project.members.all().select_related('profile')
    member_workload = []
    for member in members:
        active_count = Task.objects.filter(
            project=project,
            assigned_to=member,
            status='in_progress'
        ).count()
        member_workload.append({
            'user': member,
            'active_count': active_count,
            'overloaded': active_count > 5,
        })

    # Comments
    board_comments = project.comments.select_related('author', 'author__profile').order_by('-created_at')

    todo_count = project.tasks.filter(status='todo').count()
    in_progress_count = project.tasks.filter(status='in_progress').count()
    done_count = project.tasks.filter(status='done').count()

    from comments.forms import CommentForm
    comment_form = CommentForm()

    columns = [
        ('todo',        'To Do',       todo_tasks,        todo_count,        'bg-slate-400'),
        ('in_progress', 'In Progress', in_progress_tasks, in_progress_count, 'bg-amber-400'),
        ('done',        'Done',        done_tasks,        done_count,        'bg-emerald-400'),
    ]

    context = {
        'project': project,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
        'todo_count': todo_count,
        'in_progress_count': in_progress_count,
        'done_count': done_count,
        'member_workload': member_workload,
        'board_comments': board_comments,
        'comment_form': comment_form,
        'priority_filter': priority_filter,
        'project_members': project.members.all(),
        'columns': columns,
    }
    return render(request, 'projects/board.html', context)


@login_required
def project_settings(request, pk):
    project = get_project_or_403(pk, request.user)
    # Only owner or admin can edit settings
    role = project.get_member_role(request.user)
    if role not in ('owner', 'admin'):
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('projects:board', pk=pk)

    add_member_form = AddMemberForm(project)
    edit_form = ProjectForm(instance=project)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'edit':
            edit_form = ProjectForm(request.POST, instance=project)
            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, 'Project updated.')
                return redirect('projects:settings', pk=pk)
        elif action == 'add_member':
            add_member_form = AddMemberForm(project, request.POST)
            if add_member_form.is_valid():
                username = add_member_form.cleaned_data['username']
                role = add_member_form.cleaned_data['role']
                user = User.objects.get(username=username)
                ProjectMember.objects.create(project=project, user=user, role=role)
                messages.success(request, f'{username} added to the project.')
                return redirect('projects:settings', pk=pk)

    members = project.project_members.select_related('user', 'user__profile').all()
    return render(request, 'projects/settings.html', {
        'project': project,
        'add_member_form': add_member_form,
        'edit_form': edit_form,
        'members': members,
    })


@login_required
def remove_member(request, pk, user_id):
    project = get_project_or_403(pk, request.user)
    if project.owner != request.user:
        messages.error(request, 'Only the project owner can remove members.')
        return redirect('projects:settings', pk=pk)
    member = get_object_or_404(ProjectMember, project=project, user_id=user_id)
    if member.user == project.owner:
        messages.error(request, 'Cannot remove the project owner.')
        return redirect('projects:settings', pk=pk)
    member.delete()
    messages.success(request, 'Member removed.')
    return redirect('projects:settings', pk=pk)


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted.')
        return redirect('projects:list')
    return redirect('projects:settings', pk=pk)
