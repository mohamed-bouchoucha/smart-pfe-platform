from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from projects.models import Project, StatusHistory

User = get_user_model()


class ProjectWorkflowTests(TestCase):
    """Test project workflow transitions."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email='admin@test.com', username='admin',
            password='TestPass123!', role='admin',
        )
        self.supervisor = User.objects.create_user(
            email='sup@test.com', username='supervisor',
            password='TestPass123!', role='supervisor',
        )
        self.student = User.objects.create_user(
            email='stu@test.com', username='student',
            password='TestPass123!', role='student',
        )
        self.project = Project.objects.create(
            title='Test PFE', description='Description',
            domain='Web', technologies='Django,React',
            difficulty='intermediate', duration='3months',
            created_by=self.student,
        )
        self.client.force_authenticate(user=self.supervisor)

    # --- Default status ---
    def test_new_project_is_proposed(self):
        self.assertEqual(self.project.status, 'proposed')

    # --- Valid transitions ---
    def test_proposed_to_approved(self):
        resp = self.client.patch(
            f'/api/projects/{self.project.id}/transition/',
            {'status': 'approved'}, format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], 'approved')

    def test_proposed_to_rejected(self):
        resp = self.client.patch(
            f'/api/projects/{self.project.id}/transition/',
            {'status': 'rejected', 'comment': 'Hors sujet'}, format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], 'rejected')

    def test_full_workflow(self):
        """proposed → approved → in_progress → completed"""
        for next_status in ['approved', 'in_progress', 'completed']:
            resp = self.client.patch(
                f'/api/projects/{self.project.id}/transition/',
                {'status': next_status}, format='json',
            )
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertEqual(resp.data['status'], next_status)

    def test_rejected_can_be_resubmitted(self):
        self.project.transition_to('rejected', self.supervisor)
        resp = self.client.patch(
            f'/api/projects/{self.project.id}/transition/',
            {'status': 'proposed'}, format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], 'proposed')

    # --- Invalid transitions ---
    def test_proposed_to_in_progress_blocked(self):
        resp = self.client.patch(
            f'/api/projects/{self.project.id}/transition/',
            {'status': 'in_progress'}, format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_proposed_to_completed_blocked(self):
        resp = self.client.patch(
            f'/api/projects/{self.project.id}/transition/',
            {'status': 'completed'}, format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Status history ---
    def test_transition_creates_history(self):
        self.project.transition_to('approved', self.supervisor)
        history = StatusHistory.objects.filter(project=self.project)
        self.assertEqual(history.count(), 1)
        entry = history.first()
        self.assertEqual(entry.old_status, 'proposed')
        self.assertEqual(entry.new_status, 'approved')
        self.assertEqual(entry.changed_by, self.supervisor)

    def test_history_endpoint(self):
        self.project.transition_to('approved', self.supervisor)
        resp = self.client.get(f'/api/projects/{self.project.id}/history/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['results']), 1)

    # --- Allowed transitions in API response ---
    def test_api_returns_allowed_transitions(self):
        resp = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['allowed_transitions'], ['approved', 'rejected'])

    # --- Supervisor assignment ---
    def test_assign_supervisor(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.patch(
            f'/api/projects/{self.project.id}/assign/',
            {'supervisor_id': self.supervisor.id}, format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['supervisor'], self.supervisor.id)

    # --- Model properties ---
    def test_can_transition_to(self):
        self.assertTrue(self.project.can_transition_to('approved'))
        self.assertTrue(self.project.can_transition_to('rejected'))
        self.assertFalse(self.project.can_transition_to('in_progress'))
        self.assertFalse(self.project.can_transition_to('completed'))
