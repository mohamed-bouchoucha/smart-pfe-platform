from django.contrib import admin
from .models import Recommendation, Notification


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'score', 'generated_at']
    list_filter = ['score', 'generated_at']
    search_fields = ['user__username', 'project__title']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['title', 'user__username']
