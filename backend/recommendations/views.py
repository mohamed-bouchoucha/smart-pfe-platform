from rest_framework import permissions, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view

from accounts.permissions import IsAdminOrSupervisor
from .models import Recommendation, Notification
from .serializers import RecommendationSerializer, NotificationSerializer
from projects.models import Project
from conversations.models import Conversation

User = get_user_model()


@extend_schema_view(
    list=extend_schema(description="List AI-generated recommendations for the current user.")
)
class RecommendationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ViewSet for listing recommendations."""
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Recommendation.objects.none()
        return Recommendation.objects.filter(user=self.request.user)


@extend_schema_view(
    list=extend_schema(description="List generic notifications for the current user.")
)
class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ViewSet for user notifications."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    @extend_schema(
        responses={200: NotificationSerializer, 404: None},
        description="Mark a notification as read."
    )
    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        notification.is_read = True
        notification.save()
        return Response(self.get_serializer(notification).data)


class AdminStatsView(APIView):
    """Admin/Supervisor: platform statistics dashboard."""
    permission_classes = [IsAdminOrSupervisor]

    @extend_schema(description="Retrieve platform statistics for Admin/Supervisor dashboard.")
    def get(self, request):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)

        # User stats
        total_users = User.objects.count()
        students = User.objects.filter(role='student').count()
        supervisors = User.objects.filter(role='supervisor').count()
        admins = User.objects.filter(role='admin').count()
        new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
        active_today = User.objects.filter(last_login__gte=today_start).count()

        # Project stats (updated for new workflow statuses)
        total_projects = Project.objects.count()
        validated_projects = Project.objects.filter(status__in=['approved', 'in_progress', 'completed']).count()
        pending_projects = Project.objects.filter(status='proposed').count()
        projects_by_domain = dict(
            Project.objects.values_list('domain')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Conversation stats
        total_conversations = Conversation.objects.count()
        conversations_today = Conversation.objects.filter(created_at__gte=today_start).count()

        return Response({
            'users': {
                'total': total_users,
                'students': students,
                'supervisors': supervisors,
                'admins': admins,
                'new_this_week': new_users_week,
                'active_today': active_today,
            },
            'projects': {
                'total': total_projects,
                'validated': validated_projects,
                'pending': pending_projects,
                'by_domain': projects_by_domain,
            },
            'conversations': {
                'total': total_conversations,
                'today': conversations_today,
            },
        })
