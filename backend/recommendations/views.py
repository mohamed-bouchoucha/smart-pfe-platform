from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from accounts.permissions import IsAdminOrSupervisor
from .models import Recommendation, Notification
from .serializers import RecommendationSerializer, NotificationSerializer
from projects.models import Project
from conversations.models import Conversation

User = get_user_model()


class RecommendationListView(generics.ListAPIView):
    """List AI-generated recommendations for the current user."""
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user)


class NotificationListView(generics.ListAPIView):
    """List notifications for the current user."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkReadView(APIView):
    """Mark a notification as read."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)


class AdminStatsView(APIView):
    """Admin/Supervisor: platform statistics dashboard."""
    permission_classes = [IsAdminOrSupervisor]

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

        # Project stats
        total_projects = Project.objects.count()
        validated_projects = Project.objects.filter(status='validated').count()
        pending_projects = Project.objects.filter(status='draft').count()
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
