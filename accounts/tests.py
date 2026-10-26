from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile


class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='alice',
            password='Password123!',
            email='alice@example.com'
        )

    def test_profile_created_automatically_or_exists(self):
        profile, created = Profile.objects.get_or_create(user=self.user)
        self.assertEqual(profile.user.username, 'alice')
        self.assertEqual(profile.get_initials(), 'AL')

    def test_user_login_success(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'alice',
            'password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('projects:list'))

    def test_user_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'bobuser',
            'email': 'bob@example.com',
            'password1': 'SecretPass123!',
            'password2': 'SecretPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='bobuser').exists())

    def test_profile_update(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('accounts:profile'), {
            'email': 'alice_new@example.com',
            'bio': 'Full stack developer',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'alice_new@example.com')
        self.assertEqual(self.user.profile.bio, 'Full stack developer')
