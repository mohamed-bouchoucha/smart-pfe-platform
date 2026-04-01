from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project_list_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/transition/', views.ProjectTransitionView.as_view(), name='project_transition'),
    path('<int:pk>/history/', views.ProjectHistoryView.as_view(), name='project_history'),
    path('<int:pk>/assign/', views.ProjectAssignSupervisorView.as_view(), name='project_assign_supervisor'),
    path('skills/', views.SkillListView.as_view(), name='skill_list'),
    path('favorites/', views.FavoriteListCreateView.as_view(), name='favorite_list_create'),
    path('favorites/<int:pk>/', views.FavoriteDeleteView.as_view(), name='favorite_delete'),
]
