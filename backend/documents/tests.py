import tempfile
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.models import Document
from projects.models import Project

User = get_user_model()


class DocumentUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='student@test.com', username='student',
            password='TestPass123!', role='student',
        )
        self.project = Project.objects.create(
            title='Test Project', description='Desc', domain='Web',
            technologies='Django', difficulty='beginner',
            duration='3months', created_by=self.user,
        )
        self.client.force_authenticate(user=self.user)

    def test_upload_valid_file(self):
        file_content = b"Fake PDF content"
        f = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")
        
        resp = self.client.post('/api/documents/', {
            'file': f,
            'doc_type': 'cv',
            'project': self.project.id
        }, format='multipart')
        
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
        doc = Document.objects.first()
        self.assertEqual(doc.filename, 'test.pdf')
        self.assertEqual(doc.project.id, self.project.id)

    def test_upload_invalid_extension(self):
        file_content = b"Fake script content"
        f = SimpleUploadedFile("script.sh", file_content, content_type="text/plain")
        
        resp = self.client.post('/api/documents/', {
            'file': f,
            'doc_type': 'other'
        }, format='multipart')
        
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', resp.data)
        self.assertIn('Type de fichier non support', resp.data['file'][0])

    def test_upload_oversized_file(self):
        # Create a file exactly 5MB + 1 byte
        file_content = b"0" * (5 * 1024 * 1024 + 1)
        f = SimpleUploadedFile("large.pdf", file_content, content_type="application/pdf")
        
        resp = self.client.post('/api/documents/', {
            'file': f,
            'doc_type': 'report'
        }, format='multipart')
        
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', resp.data)
        self.assertIn('dépasser 5 Mo', resp.data['file'][0])

    def test_download_endpoint(self):
        f = SimpleUploadedFile("valid.pdf", b"Content", content_type="application/pdf")
        resp = self.client.post('/api/documents/', {'file': f, 'doc_type': 'other'}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        doc_id = Document.objects.order_by('-id').first().id
        
        download_resp = self.client.get(f'/api/documents/{doc_id}/download/')
        self.assertEqual(download_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(download_resp.get('Content-Disposition'), 'attachment; filename="valid.pdf"')
