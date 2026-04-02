from django.http import FileResponse
from rest_framework import permissions, status, parsers, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
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
        if getattr(self, 'action', None) == 'create':
            return DocumentUploadSerializer
        return DocumentSerializer
        
    def get_parsers(self):
        if getattr(self, 'action', None) == 'create':
            return [parsers.MultiPartParser(), parsers.FormParser()]
        return super().get_parsers()

    def perform_destroy(self, instance):
        # Delete the file from storage
        if instance.file:
            instance.file.delete(save=False)
        instance.delete()

    @extend_schema(description="Download the document file.")
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        document = self.get_object()
        if not document.file:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        response = FileResponse(document.file)
        response['Content-Disposition'] = f'attachment; filename="{document.filename}"'
        return response
