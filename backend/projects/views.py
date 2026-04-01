from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsAdminOrSupervisor, IsAdminOrSupervisorOrReadOnly
from .models import Project, Favorite, Skill
from .serializers import (
    ProjectSerializer, ProjectCreateSerializer,
    FavoriteSerializer, SkillSerializer,
)


class ProjectListCreateView(generics.ListCreateAPIView):
    """List validated projects (all) or create new project (admin/supervisor)."""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['domain', 'difficulty', 'status', 'duration']
    search_fields = ['title', 'description', 'technologies']
    ordering_fields = ['created_at', 'title']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ('admin', 'supervisor'):
            return Project.objects.all()
        return Project.objects.filter(status='validated')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a project."""
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminOrSupervisorOrReadOnly]
    queryset = Project.objects.all()


class ProjectValidateView(APIView):
    """Admin/Supervisor: validate or reject a project."""
    permission_classes = [IsAdminOrSupervisor]

    def patch(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(
                {'detail': 'Projet non trouvé.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        new_status = request.data.get('status')
        if new_status not in ['validated', 'rejected']:
            return Response(
                {'detail': 'Statut invalide. Choisir validated ou rejected.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project.status = new_status
        project.save()
        return Response(ProjectSerializer(project, context={'request': request}).data)


class FavoriteListCreateView(generics.ListCreateAPIView):
    """List or add favorites for the current user."""
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


class FavoriteDeleteView(generics.DestroyAPIView):
    """Remove a favorite."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


class SkillListView(generics.ListAPIView):
    """List all available skills."""
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Skill.objects.all()
