import json
import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import Project, ProjectMember
from tasks.models import Task


class TaskTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username='task_owner', password='Password123!')
        self.member = User.objects.create_user(username='task_member', password='Password123!')
        self.outsider = User.objects.create_user(username='task_outsider', password='Password123!')

        self.project = Project.objects.create(
            name='Kanban Task Test Project',
            owner=self.owner
        )
        ProjectMember.objects.create(project=self.project, user=self.member, role='member')

        self.task1 = Task.objects.create(
            title='Initial Task 1',
            description='Desc 1',
            status='todo',
            priority='high',
            project=self.project,
            created_by=self.owner,
            position=0
        )

    def test_task_creation_standard(self):
        self.client.login(username='task_owner', password='Password123!')
        response = self.client.post(
            reverse('tasks:create', args=[self.project.pk]),
            {
                'title': 'New Feature Task',
                'description': 'Details here',
                'status': 'in_progress',
                'priority': 'medium',
                'assigned_to': self.member.pk,
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Feature Task').exists())

    def test_task_creation_htmx(self):
        self.client.login(username='task_owner', password='Password123!')
        response = self.client.post(
            reverse('tasks:create', args=[self.project.pk]),
            {
                'title': 'HTMX Created Task',
                'description': 'Via modal',
                'status': 'todo',
                'priority': 'low',
            },
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'HTMX Created Task')

    def test_task_edit(self):
        self.client.login(username='task_owner', password='Password123!')
        response = self.client.post(
            reverse('tasks:edit', args=[self.project.pk, self.task1.pk]),
            {
                'title': 'Updated Title',
                'description': 'Updated Desc',
                'status': 'done',
                'priority': 'high',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Updated Title')
        self.assertEqual(self.task1.status, 'done')

    def test_task_move_drag_drop(self):
        self.client.login(username='task_owner', password='Password123!')
        response = self.client.post(
            reverse('tasks:move', args=[self.project.pk, self.task1.pk]),
            data=json.dumps({'status': 'in_progress', 'position': 0}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['new_status'], 'in_progress')
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'in_progress')

    def test_task_delete(self):
        self.client.login(username='task_owner', password='Password123!')
        response = self.client.post(
            reverse('tasks:delete', args=[self.project.pk, self.task1.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=self.task1.pk).exists())

    def test_task_overdue_property(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        self.task1.due_date = yesterday
        self.task1.status = 'todo'
        self.task1.save()
        self.assertTrue(self.task1.is_overdue)

        self.task1.status = 'done'
        self.task1.save()
        self.assertFalse(self.task1.is_overdue)

    def test_workload_partial(self):
        # Assign 6 active in_progress tasks to member to test overload
        for i in range(6):
            Task.objects.create(
                title=f'Workload Task {i}',
                status='in_progress',
                project=self.project,
                assigned_to=self.member,
                created_by=self.owner
            )
        self.client.login(username='task_member', password='Password123!')
        response = self.client.get(reverse('tasks:workload', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Overloaded')
        self.assertContains(response, '6')
