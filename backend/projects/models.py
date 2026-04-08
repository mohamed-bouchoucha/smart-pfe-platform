from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Skill(models.Model):
    """Technical skill (language, framework, tool, methodology)."""

    class Category(models.TextChoices):
        LANGUAGE = 'language', 'Langage'
        FRAMEWORK = 'framework', 'Framework'
        TOOL = 'tool', 'Outil'
        METHODOLOGY = 'methodology', 'Méthodologie'

    name = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=20, choices=Category.choices)

    class Meta:
        db_table = 'skills'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Project(models.Model):
    """PFE / Stage project idea."""

    class Domain(models.TextChoices):
        IA = 'IA', 'Intelligence Artificielle'
        WEB = 'Web', 'Développement Web'
        MOBILE = 'Mobile', 'Développement Mobile'
        DEVOPS = 'DevOps', 'DevOps'
        CYBERSECURITY = 'Cybersecurity', 'Cybersécurité'
        DATA_SCIENCE = 'DataScience', 'Data Science'
        IOT = 'IoT', 'Internet des Objets'
        CLOUD = 'Cloud', 'Cloud Computing'
        OTHER = 'Other', 'Autre'

    class Difficulty(models.TextChoices):
        BEGINNER = 'beginner', 'Débutant'
        INTERMEDIATE = 'intermediate', 'Intermédiaire'
        ADVANCED = 'advanced', 'Avancé'

    class Duration(models.TextChoices):
        ONE_MONTH = '1month', '1 mois'
        TWO_MONTHS = '2months', '2 mois'
        THREE_MONTHS = '3months', '3 mois'
        SIX_MONTHS = '6months', '6 mois'

    class Status(models.TextChoices):
        PROPOSED = 'proposed', 'Proposé'
        APPROVED = 'approved', 'Approuvé'
        IN_PROGRESS = 'in_progress', 'En cours'
        COMPLETED = 'completed', 'Terminé'
        REJECTED = 'rejected', 'Rejeté'

    # Valid workflow transitions: current_status -> [allowed_next_statuses]
    VALID_TRANSITIONS = {
        'proposed': ['approved', 'rejected'],
        'approved': ['in_progress', 'rejected'],
        'in_progress': ['completed'],
        'completed': [],
        'rejected': ['proposed'],  # Allow resubmission
    }

    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    description_en = models.TextField(blank=True, null=True)
    domain = models.CharField(max_length=20, choices=Domain.choices)
    technologies = models.CharField(max_length=500, help_text="Comma-separated list")
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices)
    duration = models.CharField(max_length=20, choices=Duration.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)
    company_name = models.CharField(max_length=255, blank=True)
    skills = models.ManyToManyField(Skill, through='ProjectSkill', related_name='projects', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects',
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='supervised_projects',
        limit_choices_to={'role': 'supervisor'},
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_projects',
        limit_choices_to={'role': 'student'},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def can_transition_to(self, new_status):
        """Check if transition from current status to new_status is valid."""
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])

    def transition_to(self, new_status, changed_by):
        """Transition to a new status with validation and history tracking."""
        if not self.can_transition_to(new_status):
            raise ValidationError(
                f"Transition de '{self.get_status_display()}' vers "
                f"'{dict(self.Status.choices).get(new_status, new_status)}' non autorisée."
            )
        old_status = self.status
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])
        StatusHistory.objects.create(
            project=self,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
        )
        return self

    @property
    def average_rating(self):
        """Calculate average rating for this project."""
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    @property
    def review_count(self):
        """Get the number of reviews."""
        return self.reviews.count()


class StatusHistory(models.Model):
    """Audit trail for project status changes."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = 'status_history'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.project.title}: {self.old_status} → {self.new_status}"


class ProjectSkill(models.Model):
    """Junction table: skills required by a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    is_required = models.BooleanField(default=True)

    class Meta:
        db_table = 'project_skills'
        unique_together = ['project', 'skill']


class Favorite(models.Model):
    """User's bookmarked projects."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='favorited_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        unique_together = ['user', 'project']
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} ❤ {self.project.title}"


class Review(models.Model):
    """Rating and comment left by a student after completing a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Project rating from 1 to 5 stars"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_reviews'
        unique_together = ['project', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.project.title} ({self.rating}★)"
