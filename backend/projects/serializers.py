from rest_framework import serializers
from .models import Project, Skill, Favorite, ProjectSkill, StatusHistory, Review, Application


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'name_en', 'category']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        # If language is English and name_en is provided, use it
        if request and getattr(request, 'LANGUAGE_CODE', 'fr').startswith('en') and instance.name_en:
            ret['name'] = instance.name_en
        return ret


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
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, default=None)
    application_status = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'title_en', 'description', 'description_en', 'domain', 'technologies',
            'difficulty', 'duration', 'status', 'company_name',
            'skills', 'created_by', 'created_by_name',
            'supervisor', 'supervisor_name',
            'assigned_to', 'assigned_to_name',
            'is_favorited', 'allowed_transitions',
            'average_rating', 'review_count',
            'application_status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        # Dynamic translation for title and description
        if request and getattr(request, 'LANGUAGE_CODE', 'fr').startswith('en'):
            if instance.title_en:
                ret['title'] = instance.title_en
            if instance.description_en:
                ret['description'] = instance.description_en
        return ret

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, project=obj).exists()
        return False

    def get_allowed_transitions(self, obj):
        return Project.VALID_TRANSITIONS.get(obj.status, [])

    def get_application_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            app = Application.objects.filter(user=request.user, project=obj).first()
            return app.status if app else None
        return None


class ProjectCreateSerializer(serializers.ModelSerializer):
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'title_en', 'description', 'description_en', 'domain', 'technologies',
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


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'project', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationSerializer(serializers.ModelSerializer):
    project_details = ProjectSerializer(source='project', read_only=True)
    student_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'project', 'project_details', 'user', 'student_name', 
            'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
