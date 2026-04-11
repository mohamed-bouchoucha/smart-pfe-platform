import django_filters
from .models import Project, Skill

class ProjectFilter(django_filters.FilterSet):
    """Advanced filtering for PFE projects."""
    
    # Multi-choice filtering for domains
    domain = django_filters.AllValuesMultipleFilter(field_name='domain')
    
    # Range filtering for created_at
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Multi-choice filtering for skills
    skills = django_filters.ModelMultipleChoiceFilter(
        field_name='skills',
        queryset=Skill.objects.all(),
    )
    
    # Minimum and maximum duration if needed (though choices are fixed)
    # Search for specific technologies (partial match)
    tech = django_filters.CharFilter(field_name='technologies', lookup_expr='icontains')

    class Meta:
        model = Project
        fields = ['domain', 'difficulty', 'duration', 'status', 'company_name']
