from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import Project, ProjectMember


class ProjectTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='owner_user', password='Password123!')
        self.member = User.objects.create_user(username='member_user', password='Password123!')
        self.outsider = User.objects.create_user(username='outsider_user', password='Password123!')

        self.project = Project.objects.create(
            name='Alpha Project',
            description='Test Alpha Project Description',
            owner=self.owner
        )
        ProjectMember.objects.create(project=self.project, user=self.member, role='member')

    def test_project_list_authenticated(self):
        self.client.login(username='owner_user', password='Password123!')
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alpha Project')

    def test_project_create(self):
        self.client.login(username='owner_user', password='Password123!')
        response = self.client.post(reverse('projects:create'), {
            'name': 'Beta Project',
            'description': 'Second project',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name='Beta Project').exists())

    def test_project_board_access_member(self):
        self.client.login(username='member_user', password='Password123!')
        response = self.client.get(reverse('projects:board', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)

    def test_project_board_access_denied_outsider(self):
        self.client.login(username='outsider_user', password='Password123!')
        response = self.client.get(reverse('projects:board', args=[self.project.pk]))
        self.assertEqual(response.status_code, 403)

    def test_add_and_remove_member(self):
        self.client.login(username='owner_user', password='Password123!')
        # Add outsider as member via settings view
        response = self.client.post(
            reverse('projects:settings', args=[self.project.pk]),
            {'action': 'add_member', 'username': 'outsider_user', 'role': 'member'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.project.is_member(self.outsider))

        # Remove member
        response = self.client.post(
            reverse('projects:remove_member', args=[self.project.pk, self.outsider.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.project.is_member(self.outsider))
