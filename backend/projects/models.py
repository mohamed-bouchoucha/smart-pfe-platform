from django.db import models
from django.conf import settings


class Skill(models.Model):
    """Technical skill (language, framework, tool, methodology)."""

    class Category(models.TextChoices):
        LANGUAGE = 'language', 'Langage'
        FRAMEWORK = 'framework', 'Framework'
        TOOL = 'tool', 'Outil'
        METHODOLOGY = 'methodology', 'Méthodologie'

    name = models.CharField(max_length=100, unique=True)
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
        DRAFT = 'draft', 'Brouillon'
        VALIDATED = 'validated', 'Validé'
        REJECTED = 'rejected', 'Rejeté'

    title = models.CharField(max_length=255)
    description = models.TextField()
    domain = models.CharField(max_length=20, choices=Domain.choices)
    technologies = models.CharField(max_length=500, help_text="Comma-separated list")
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices)
    duration = models.CharField(max_length=20, choices=Duration.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    company_name = models.CharField(max_length=255, blank=True)
    skills = models.ManyToManyField(Skill, through='ProjectSkill', related_name='projects', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


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
