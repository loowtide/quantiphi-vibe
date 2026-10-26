from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from projects.models import Project
from .models import Comment
from .forms import CommentForm


@login_required
@require_POST
def add_comment(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not project.is_member(request.user):
        raise PermissionDenied

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.project = project
        comment.author = request.user
        comment.save()

        if request.htmx:
            comments = project.comments.select_related('author', 'author__profile').all()
            return render(request, 'comments/partials/comment_list.html', {
                'board_comments': comments,
                'project': project,
                'comment_form': CommentForm(),
            })

    # On error, re-render with form
    if request.htmx:
        comments = project.comments.select_related('author', 'author__profile').all()
        return render(request, 'comments/partials/comment_list.html', {
            'board_comments': comments,
            'project': project,
            'comment_form': form,
        }, status=422)

    return redirect('projects:board', pk=project_id)


@login_required
@require_POST
def delete_comment(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    comment = get_object_or_404(Comment, pk=pk, project=project)

    # Only the author or project owner can delete
    if comment.author != request.user and project.owner != request.user:
        raise PermissionDenied

    comment.delete()

    if request.htmx:
        comments = project.comments.select_related('author', 'author__profile').all()
        return render(request, 'comments/partials/comment_list.html', {
            'board_comments': comments,
            'project': project,
            'comment_form': CommentForm(),
        })
    return redirect('projects:board', pk=project_id)
