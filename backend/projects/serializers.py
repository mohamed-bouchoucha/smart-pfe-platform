from rest_framework import serializers
from .models import Project, Skill, Favorite, ProjectSkill, StatusHistory


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category']


class StatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)

    class Meta:
        model = StatusHistory
        fields = ['id', 'old_status', 'new_status', 'changed_by', 'changed_by_name', 'changed_at', 'comment']
        read_only_fields = fields


class ProjectSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.get_full_name', read_only=True, default=None)
    is_favorited = serializers.SerializerMethodField()
    allowed_transitions = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'domain', 'technologies',
            'difficulty', 'duration', 'status', 'company_name',
            'skills', 'created_by', 'created_by_name',
            'supervisor', 'supervisor_name',
            'is_favorited', 'allowed_transitions',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, project=obj).exists()
        return False

    def get_allowed_transitions(self, obj):
        return Project.VALID_TRANSITIONS.get(obj.status, [])


class ProjectCreateSerializer(serializers.ModelSerializer):
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'domain', 'technologies',
            'difficulty', 'duration', 'company_name', 'supervisor', 'skill_ids',
        ]

    def create(self, validated_data):
        skill_ids = validated_data.pop('skill_ids', [])
        project = Project.objects.create(**validated_data)
        for skill_id in skill_ids:
            ProjectSkill.objects.create(project=project, skill_id=skill_id)
        return project


class ProjectTransitionSerializer(serializers.Serializer):
    """Serializer for status transition requests."""
    status = serializers.ChoiceField(choices=Project.Status.choices)
    comment = serializers.CharField(required=False, default='')


class FavoriteSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'project', 'project_id', 'saved_at']
        read_only_fields = ['id', 'saved_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_project_id(self, value):
        if not Project.objects.filter(id=value).exclude(status='rejected').exists():
            raise serializers.ValidationError("Projet non trouvé ou rejeté.")
        if Favorite.objects.filter(
            user=self.context['request'].user, project_id=value
        ).exists():
            raise serializers.ValidationError("Projet déjà dans vos favoris.")
        return value
