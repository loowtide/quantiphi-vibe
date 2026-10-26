from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import Project, ProjectMember
from comments.models import Comment


class CommentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='c_owner', password='Password123!')
        self.member = User.objects.create_user(username='c_member', password='Password123!')
        self.outsider = User.objects.create_user(username='c_outsider', password='Password123!')

        self.project = Project.objects.create(name='Comment Project', owner=self.owner)
        ProjectMember.objects.create(project=self.project, user=self.member, role='member')

    def test_add_comment(self):
        self.client.login(username='c_member', password='Password123!')
        response = self.client.post(
            reverse('comments:add', args=[self.project.pk]),
            {'content': 'Looking great! Working on this now.'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content='Looking great! Working on this now.').exists())

    def test_outsider_cannot_comment(self):
        self.client.login(username='c_outsider', password='Password123!')
        response = self.client.post(
            reverse('comments:add', args=[self.project.pk]),
            {'content': 'Unauthorized comment'}
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_comment_by_author(self):
        comment = Comment.objects.create(
            project=self.project, author=self.member, content='Delete me'
        )
        self.client.login(username='c_member', password='Password123!')
        response = self.client.post(
            reverse('comments:delete', args=[self.project.pk, comment.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
