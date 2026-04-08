from rest_framework import permissions, status, filters, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse

from accounts.permissions import IsAdminOrSupervisor, IsAdminOrSupervisorOrReadOnly
from .models import Project, Favorite, Skill, StatusHistory, Review, Application
from .filters import ProjectFilter
from .serializers import (
    ProjectSerializer, ProjectCreateSerializer,
    FavoriteSerializer, SkillSerializer,
    ProjectTransitionSerializer, StatusHistorySerializer,
    ReviewSerializer, ApplicationSerializer,
)


@extend_schema_view(
    list=extend_schema(description="List projects (filtered based on user role)."),
    create=extend_schema(description="Create a new project.", responses={201: ProjectSerializer}),
    retrieve=extend_schema(description="Get details of a specific project."),
    update=extend_schema(description="Update an entire project (Admin/Supervisor)."),
    partial_update=extend_schema(description="Partially update a project (Admin/Supervisor)."),
    destroy=extend_schema(description="Delete a project (Admin/Supervisor)."),
)
class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Projects."""
    permission_classes = [IsAdminOrSupervisorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = [
        'title', 'title_en', 'description', 'description_en', 
        'technologies', 'company_name', 'created_by__username'
    ]
    ordering_fields = ['created_at', 'title', 'difficulty']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Project.objects.none()
            
        if user.role in ('admin', 'supervisor'):
            return Project.objects.select_related('created_by', 'supervisor').all()
        # Students see approved + in_progress + completed projects, and their own
        return Project.objects.select_related('created_by', 'supervisor').filter(
            status__in=['approved', 'in_progress', 'completed']
        ) | Project.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(
        request=ProjectTransitionSerializer,
        responses={200: ProjectSerializer, 400: OpenApiResponse(description="Invalid transition")},
        description="Transition a project to a new status (admin/supervisor only)."
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminOrSupervisor])
    def transition(self, request, pk=None):
        try:
            project = self.get_object()
        except Project.DoesNotExist:
            return Response({'detail': 'Projet non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']
        comment = serializer.validated_data.get('comment', '')

        try:
            project.transition_to(new_status, changed_by=request.user)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

        if comment:
            history = project.status_history.first()
            if history:
                history.comment = comment
                history.save(update_fields=['comment'])

        return Response(self.get_serializer(project).data)

    @extend_schema(
        responses={200: StatusHistorySerializer(many=True)},
        description="View status change history for a project."
    )
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def history(self, request, pk=None):
        project_history = StatusHistory.objects.filter(
            project_id=pk
        ).select_related('changed_by')
        
        page = self.paginate_queryset(project_history)
        if page is not None:
            serializer = StatusHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = StatusHistorySerializer(project_history, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=OpenApiParameter("supervisor_id", int, description="ID of the supervisor to assign"),
        responses={200: ProjectSerializer, 404: OpenApiResponse(description="Supervisor not found")},
        description="Assign a supervisor to a project (admin only)."
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminOrSupervisor])
    def assign(self, request, pk=None):
        try:
            project = self.get_object()
        except Project.DoesNotExist:
            return Response({'detail': 'Projet non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
            
        supervisor_id = request.data.get('supervisor_id')
        if supervisor_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                supervisor = User.objects.get(pk=supervisor_id, role='supervisor')
            except User.DoesNotExist:
                return Response({'detail': 'Encadrant non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
            project.supervisor = supervisor
        else:
            project.supervisor = None
        project.save(update_fields=['supervisor', 'updated_at'])
        return Response(self.get_serializer(project).data)

    @extend_schema(
        responses={200: OpenApiResponse(description="Skill gap data for radar chart")},
        description="Calculate skill gap between current user and the project."
    )
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def skill_gap(self, request, pk=None):
        project = self.get_object()
        user = request.user
        
        # Get project skills (names)
        project_skills = project.skills.all()
        labels = [s.name for s in project_skills]
        
        # Get user skills (names)
        user_skills = set(user.skills.values_list('name', flat=True))
        
        user_scores = [1 if s.name in user_skills else 0 for s in project_skills]
        required_scores = [1 for _ in project_skills]
        missing_skills = [s.name for s in project_skills if s.name not in user_skills]
        
        return Response({
            'labels': labels,
            'user_scores': user_scores,
            'required_scores': required_scores,
            'missing_skills': missing_skills,
        })


@extend_schema_view(
    list=extend_schema(description="List favorites for the current user."),
    create=extend_schema(description="Add a project to favorites."),
    destroy=extend_schema(description="Remove a favorite.")
)
class FavoriteViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for tracking favorite projects."""
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user)


@extend_schema_view(
    list=extend_schema(description="List all available skills.")
)
class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Skills."""
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Skill.objects.all()


@extend_schema_view(
    list=extend_schema(description="List reviews for a specific project."),
    create=extend_schema(description="Create a review (Student only).")
)
class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Project Reviews."""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        if project_id:
            return Review.objects.filter(project_id=project_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data['project']

        # Validation: Only students
        if not user.is_student:
            raise ValidationError("Seuls les étudiants peuvent laisser des avis.")

        # Validation: Project must be completed
        if project.status != 'completed':
            raise ValidationError("Vous ne pouvez noter que les projets terminés.")

        # Validation: User must be assigned to the project
        if project.assigned_to != user:
            raise ValidationError("Vous ne pouvez noter que les projets qui vous ont été assignés.")

        serializer.save(user=user)


@extend_schema_view(
    list=extend_schema(description="List applications for the current student."),
    create=extend_schema(description="Apply for a project."),
    partial_update=extend_schema(description="Update application status.")
)
class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Project Applications."""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Application.objects.none()
        
        if user.is_student:
            return Application.objects.filter(user=user).select_related('project')
        # Admins and Supervisors can see all applications
        return Application.objects.all().select_related('project', 'user')

    def perform_create(self, serializer):
        # Additional validation: check if already applied
        project = serializer.validated_data['project']
        if Application.objects.filter(user=self.request.user, project=project).exists():
            raise ValidationError("Vous avez déjà une candidature en cours pour ce projet.")
        serializer.save(user=self.request.user)
