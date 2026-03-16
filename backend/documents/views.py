from rest_framework import generics, permissions, status, parsers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer


class DocumentListView(generics.ListAPIView):
    """List user's uploaded documents."""
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)


class DocumentUploadView(generics.CreateAPIView):
    """Upload a new document."""
    serializer_class = DocumentUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]


class DocumentDeleteView(generics.DestroyAPIView):
    """Delete a document."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # Delete the file from storage
        if instance.file:
            instance.file.delete(save=False)
        instance.delete()
