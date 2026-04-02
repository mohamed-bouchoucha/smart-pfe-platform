from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class RoleBasedAuthTests(TestCase):
    """Test role-based authentication and permissions."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email='admin@test.com', username='admin',
            password='TestPass123!', role='admin',
        )
        self.supervisor = User.objects.create_user(
            email='supervisor@test.com', username='supervisor',
            password='TestPass123!', role='supervisor',
        )
        self.student = User.objects.create_user(
            email='student@test.com', username='student',
            password='TestPass123!', role='student',
        )

    def _auth(self, user):
        self.client.force_authenticate(user=user)

    # --- Registration with role ---
    def test_register_student(self):
        resp = self.client.post('/api/auth/register/', {
            'email': 'new@test.com', 'username': 'newuser',
            'password': 'StrongPass123!', 'password_confirm': 'StrongPass123!',
            'role': 'student',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['user']['role'], 'student')

    def test_register_supervisor(self):
        resp = self.client.post('/api/auth/register/', {
            'email': 'sup@test.com', 'username': 'newsup',
            'password': 'StrongPass123!', 'password_confirm': 'StrongPass123!',
            'role': 'supervisor',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['user']['role'], 'supervisor')

    def test_register_admin_blocked(self):
        """Users cannot self-assign admin role."""
        resp = self.client.post('/api/auth/register/', {
            'email': 'hack@test.com', 'username': 'hacker',
            'password': 'StrongPass123!', 'password_confirm': 'StrongPass123!',
            'role': 'admin',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # --- User list (admin only) ---
    def test_admin_can_list_users(self):
        self._auth(self.admin)
        resp = self.client.get('/api/auth/users/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_student_cannot_list_users(self):
        self._auth(self.student)
        resp = self.client.get('/api/auth/users/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_supervisor_cannot_list_users(self):
        self._auth(self.supervisor)
        resp = self.client.get('/api/auth/users/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # --- Supervisor list (all authenticated) ---
    def test_student_can_list_supervisors(self):
        self._auth(self.student)
        resp = self.client.get('/api/auth/users/supervisors/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- Project validation (admin/supervisor only) ---
    def test_supervisor_can_transition_project(self):
        from projects.models import Project
        project = Project.objects.create(
            title='Test', description='Desc', domain='Web',
            technologies='Django', difficulty='beginner',
            duration='3months', created_by=self.admin,
        )
        self._auth(self.supervisor)
        resp = self.client.patch(
            f'/api/projects/{project.id}/transition/',
            {'status': 'approved'}, format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], 'approved')

    def test_student_cannot_transition_project(self):
        from projects.models import Project
        project = Project.objects.create(
            title='Test2', description='Desc', domain='Web',
            technologies='Django', difficulty='beginner',
            duration='3months', created_by=self.admin,
        )
        self._auth(self.student)
        resp = self.client.patch(
            f'/api/projects/{project.id}/transition/',
            {'status': 'approved'}, format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # --- Admin stats (admin/supervisor) ---
    def test_supervisor_can_view_stats(self):
        self._auth(self.supervisor)
        resp = self.client.get('/api/admin/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('supervisors', resp.data['users'])

    def test_student_cannot_view_stats(self):
        self._auth(self.student)
        resp = self.client.get('/api/admin/stats/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # --- Model properties ---
    def test_role_properties(self):
        self.assertTrue(self.admin.is_admin)
        self.assertFalse(self.admin.is_supervisor)
        self.assertTrue(self.supervisor.is_supervisor)
        self.assertFalse(self.supervisor.is_student)
        self.assertTrue(self.student.is_student)
        self.assertFalse(self.student.is_admin)
