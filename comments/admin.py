from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['project', 'author', 'content_snippet', 'created_at']
    search_fields = ['content', 'author__username', 'project__name']
    list_filter = ['created_at']

    def content_snippet(self, obj):
        return obj.content[:50]
    content_snippet.short_description = 'Content'
