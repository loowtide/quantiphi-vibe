import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import Project, ProjectMember
from tasks.models import Task
from notifications.models import Notification, PingCooldown


class NotificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.alice = User.objects.create_user(username='alice_notif', password='Password123!')
        self.bob = User.objects.create_user(username='bob_notif', password='Password123!')

        self.project = Project.objects.create(name='Notif Project', owner=self.alice)
        ProjectMember.objects.create(project=self.project, user=self.bob, role='member')

        self.task = Task.objects.create(
            title='Backend API Implementation',
            project=self.project,
            assigned_to=self.bob,
            created_by=self.alice,
            due_date=datetime.date.today() + datetime.timedelta(days=2)
        )

    def test_ping_deadline_success(self):
        self.client.login(username='alice_notif', password='Password123!')
        response = self.client.post(
            reverse('notifications:ping', args=[self.project.pk, self.task.pk]),
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ping sent!')
        self.assertTrue(Notification.objects.filter(recipient=self.bob, notification_type='ping').exists())

    def test_cannot_ping_self(self):
        self.client.login(username='bob_notif', password='Password123!')
        response = self.client.post(
            reverse('notifications:ping', args=[self.project.pk, self.task.pk]),
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'cannot ping yourself', status_code=400)

    def test_ping_cooldown(self):
        self.client.login(username='alice_notif', password='Password123!')
        # First ping
        self.client.post(
            reverse('notifications:ping', args=[self.project.pk, self.task.pk]),
            HTTP_HX_REQUEST='true'
        )
        # Second immediate ping should hit cooldown
        response = self.client.post(
            reverse('notifications:ping', args=[self.project.pk, self.task.pk]),
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, 'Wait', status_code=429)

    def test_mark_notifications_read(self):
        notif = Notification.objects.create(
            recipient=self.bob,
            sender=self.alice,
            message='Test notification',
            notification_type='ping',
            is_read=False
        )
        self.client.login(username='bob_notif', password='Password123!')
        response = self.client.post(reverse('notifications:mark_read', args=[notif.pk]))
        self.assertEqual(response.status_code, 302)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
