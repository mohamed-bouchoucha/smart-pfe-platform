from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsAdminOrSupervisor, IsAdminOrSupervisorOrReadOnly
from .models import Project, Favorite, Skill, StatusHistory
from .serializers import (
    ProjectSerializer, ProjectCreateSerializer,
    FavoriteSerializer, SkillSerializer,
    ProjectTransitionSerializer, StatusHistorySerializer,
)


class ProjectListCreateView(generics.ListCreateAPIView):
    """List projects or create new project."""
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
            return Project.objects.select_related('created_by', 'supervisor').all()
        # Students see approved + in_progress + completed projects, and their own
        return Project.objects.select_related('created_by', 'supervisor').filter(
            status__in=['approved', 'in_progress', 'completed']
        ) | Project.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a project."""
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminOrSupervisorOrReadOnly]
    queryset = Project.objects.select_related('created_by', 'supervisor').all()


class ProjectTransitionView(APIView):
    """Transition a project to a new status (admin/supervisor only)."""
    permission_classes = [IsAdminOrSupervisor]

    def patch(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(
                {'detail': 'Projet non trouvé.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']
        comment = serializer.validated_data.get('comment', '')

        try:
            project.transition_to(new_status, changed_by=request.user)
        except ValidationError as e:
            return Response(
                {'detail': e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save comment on the history entry
        if comment:
            history = project.status_history.first()
            if history:
                history.comment = comment
                history.save(update_fields=['comment'])

        return Response(ProjectSerializer(project, context={'request': request}).data)


class ProjectHistoryView(generics.ListAPIView):
    """View status change history for a project."""
    serializer_class = StatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StatusHistory.objects.filter(
            project_id=self.kwargs['pk']
        ).select_related('changed_by')


class ProjectAssignSupervisorView(APIView):
    """Assign a supervisor to a project (admin only)."""
    permission_classes = [IsAdminOrSupervisor]

    def patch(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(
                {'detail': 'Projet non trouvé.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        supervisor_id = request.data.get('supervisor_id')
        if supervisor_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                supervisor = User.objects.get(pk=supervisor_id, role='supervisor')
            except User.DoesNotExist:
                return Response(
                    {'detail': 'Encadrant non trouvé.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            project.supervisor = supervisor
        else:
            project.supervisor = None
        project.save(update_fields=['supervisor', 'updated_at'])
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
