from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

VALID = {
    'first_name': 'Juan', 'last_name': 'Dela Cruz', 'username': 'juan',
    'email': 'juan@example.com', 'contact_number': '09171234567',
    'platforms': ['MAXIM', 'GRAB'],
    'password1': 'Str0ng-pass-123', 'password2': 'Str0ng-pass-123',
}


class RegistrationTests(TestCase):
    def test_register_creates_rider_with_hashed_password(self):
        resp = self.client.post(reverse('accounts:register'), VALID, follow=True)
        self.assertContains(resp, 'Account created')
        user = User.objects.get(username='juan')
        self.assertEqual(user.role, User.Role.RIDER)
        self.assertNotEqual(user.password, VALID['password1'])
        self.assertTrue(user.check_password(VALID['password1']))
        self.assertEqual(user.platform_list, ['MAXIM', 'GRAB'])

    def test_validation_errors(self):
        User.objects.create_user('taken', 'taken@example.com', 'x')
        data = {**VALID, 'username': 'TAKEN', 'email': 'TAKEN@example.com', 'password2': 'nope'}
        resp = self.client.post(reverse('accounts:register'), data)
        form = resp.context['form']
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)

    def test_invalid_email_and_required(self):
        resp = self.client.post(reverse('accounts:register'), {**VALID, 'email': 'bad', 'first_name': ''})
        self.assertIn('email', resp.context['form'].errors)
        self.assertIn('first_name', resp.context['form'].errors)


class AuthAndRoleTests(TestCase):
    def setUp(self):
        self.rider = User.objects.create_user('rider', 'rider@example.com', 'pass-12345', role=User.Role.RIDER)
        self.admin = User.objects.create_superuser('boss', 'boss@example.com', 'pass-12345')

    def test_superuser_is_admin_role(self):
        self.assertEqual(self.admin.role, User.Role.ADMIN)

    def test_login_with_username_or_email_and_redirect_by_role(self):
        resp = self.client.post(reverse('accounts:login'), {'username': 'rider@example.com', 'password': 'pass-12345'}, follow=True)
        self.assertRedirects(resp, reverse('accounts:rider_dashboard'))
        self.client.post(reverse('accounts:logout'))
        resp = self.client.post(reverse('accounts:login'), {'username': 'boss', 'password': 'pass-12345'}, follow=True)
        self.assertRedirects(resp, reverse('accounts:admin_dashboard'))

    def test_invalid_login_shows_error(self):
        resp = self.client.post(reverse('accounts:login'), {'username': 'rider', 'password': 'wrong'})
        self.assertContains(resp, 'Invalid username/email or password')

    def test_protected_pages_redirect_to_login(self):
        for name in ('dashboard', 'rider_dashboard', 'admin_dashboard', 'profile', 'profile_edit'):
            resp = self.client.get(reverse(f'accounts:{name}'))
            self.assertRedirects(resp, f"{reverse('accounts:login')}?next={reverse(f'accounts:{name}')}")

    def test_rider_cannot_open_admin_dashboard_and_vice_versa(self):
        self.client.force_login(self.rider)
        self.assertRedirects(self.client.get(reverse('accounts:admin_dashboard')), reverse('accounts:dashboard'), target_status_code=302)
        self.client.force_login(self.admin)
        self.assertRedirects(self.client.get(reverse('accounts:rider_dashboard')), reverse('accounts:dashboard'), target_status_code=302)

    def test_logout_ends_session(self):
        self.client.force_login(self.rider)
        self.client.post(reverse('accounts:logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.get(reverse('accounts:profile')).status_code, 302)


class ProfileTests(TestCase):
    def setUp(self):
        self.rider = User.objects.create_user('rider', 'rider@example.com', 'pass-12345')
        self.other = User.objects.create_user('other', 'other@example.com', 'pass-12345')

    def test_update_own_profile(self):
        self.client.force_login(self.rider)
        resp = self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Ria', 'last_name': 'Santos', 'email': 'ria@example.com',
            'contact_number': '+639181234567', 'platforms': ['MOVEIT'],
            'vehicle_type': 'Motorcycle', 'plate_number': 'ABC 1234',
        }, follow=True)
        self.assertContains(resp, 'Profile updated')
        self.rider.refresh_from_db()
        self.assertEqual(self.rider.email, 'ria@example.com')
        self.assertEqual(self.rider.platform_list, ['MOVEIT'])
        self.other.refresh_from_db()
        self.assertEqual(self.other.email, 'other@example.com')

    def test_cannot_take_someone_elses_email(self):
        self.client.force_login(self.rider)
        resp = self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'A', 'last_name': 'B', 'email': 'other@example.com',
        })
        self.assertIn('email', resp.context['form'].errors)
