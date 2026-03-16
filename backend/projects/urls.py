from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project_list_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/validate/', views.ProjectValidateView.as_view(), name='project_validate'),
    path('skills/', views.SkillListView.as_view(), name='skill_list'),
    path('favorites/', views.FavoriteListCreateView.as_view(), name='favorite_list_create'),
    path('favorites/<int:pk>/', views.FavoriteDeleteView.as_view(), name='favorite_delete'),
]
