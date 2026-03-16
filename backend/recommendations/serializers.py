from rest_framework import serializers
from .models import Recommendation, Notification
from projects.serializers import ProjectSerializer


class RecommendationSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = ['id', 'project', 'score', 'reason', 'matched_skills', 'generated_at']
        read_only_fields = ['id', 'generated_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'type', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
