from rest_framework import permissions, status, parsers, viewsets, mixins
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer


@extend_schema_view(
    list=extend_schema(description="List user's uploaded documents."),
    create=extend_schema(
        description="Upload a new document.", 
        request=DocumentUploadSerializer,
        responses={201: DocumentSerializer}
    ),
    destroy=extend_schema(description="Delete a document.")
)
class DocumentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for Documents."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Document.objects.none()
        return Document.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentUploadSerializer
        return DocumentSerializer
        
    def get_parsers(self):
        if self.action == 'create':
            return [parsers.MultiPartParser(), parsers.FormParser()]
        return super().get_parsers()

    def perform_destroy(self, instance):
        # Delete the file from storage
        if instance.file:
            instance.file.delete(save=False)
        instance.delete()
