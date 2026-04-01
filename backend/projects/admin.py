from django.contrib import admin
from .models import Project, Skill, ProjectSkill, Favorite, StatusHistory


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']


class ProjectSkillInline(admin.TabularInline):
    model = ProjectSkill
    extra = 1


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'changed_by', 'changed_at', 'comment']
    can_delete = False


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'domain', 'difficulty', 'status', 'supervisor', 'created_by', 'created_at']
    list_filter = ['domain', 'difficulty', 'status', 'supervisor']
    search_fields = ['title', 'description', 'technologies']
    inlines = [ProjectSkillInline, StatusHistoryInline]
    actions = ['approve_projects', 'reject_projects']

    @admin.action(description='Approuver les projets sélectionnés')
    def approve_projects(self, request, queryset):
        for project in queryset.filter(status='proposed'):
            project.transition_to('approved', changed_by=request.user)

    @admin.action(description='Rejeter les projets sélectionnés')
    def reject_projects(self, request, queryset):
        for project in queryset.exclude(status__in=['completed', 'rejected']):
            project.transition_to('rejected', changed_by=request.user)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'saved_at']
    list_filter = ['saved_at']


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['project', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['new_status', 'changed_at']
    readonly_fields = ['project', 'old_status', 'new_status', 'changed_by', 'changed_at', 'comment']
