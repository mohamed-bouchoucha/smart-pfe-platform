from django.db import models
from django.conf import settings


class Recommendation(models.Model):
    """AI-generated project recommendation for a user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='recommendations',
    )
    score = models.FloatField(help_text="Relevance score 0.0 - 1.0")
    reason = models.TextField(blank=True)
    matched_skills = models.JSONField(default=list, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendations'
        ordering = ['-score', '-generated_at']
        unique_together = ['user', 'project']

    def __str__(self):
        return f"{self.user.username} → {self.project.title} ({self.score:.0%})"


class Notification(models.Model):
    """User notification."""

    class Type(models.TextChoices):
        INFO = 'info', 'Information'
        SUCCESS = 'success', 'Succès'
        WARNING = 'warning', 'Avertissement'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.INFO)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.type}] {self.title}"
