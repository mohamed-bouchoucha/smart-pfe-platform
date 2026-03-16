from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """Chat session between a user and the AI assistant."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations',
    )
    title = models.CharField(max_length=255, default='Nouvelle conversation')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} — {self.user.username}"


class Message(models.Model):
    """Individual message in a conversation."""

    class Sender(models.TextChoices):
        USER = 'user', 'Utilisateur'
        ASSISTANT = 'assistant', 'Assistant IA'

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.CharField(max_length=10, choices=Sender.choices)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.sender}] {self.content[:50]}..."
