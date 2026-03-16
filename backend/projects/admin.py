from django.contrib import admin
from .models import Project, Skill, ProjectSkill, Favorite


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']


class ProjectSkillInline(admin.TabularInline):
    model = ProjectSkill
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'domain', 'difficulty', 'status', 'created_by', 'created_at']
    list_filter = ['domain', 'difficulty', 'status']
    search_fields = ['title', 'description', 'technologies']
    inlines = [ProjectSkillInline]
    actions = ['validate_projects', 'reject_projects']

    @admin.action(description='Valider les projets sélectionnés')
    def validate_projects(self, request, queryset):
        queryset.update(status='validated')

    @admin.action(description='Rejeter les projets sélectionnés')
    def reject_projects(self, request, queryset):
        queryset.update(status='rejected')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'saved_at']
    list_filter = ['saved_at']
