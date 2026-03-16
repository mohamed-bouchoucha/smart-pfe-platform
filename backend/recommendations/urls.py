from django.urls import path
from . import views

urlpatterns = [
    path('', views.RecommendationListView.as_view(), name='recommendation_list'),
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/read/', views.NotificationMarkReadView.as_view(), name='notification_mark_read'),
    path('admin/stats/', views.AdminStatsView.as_view(), name='admin_stats'),
]
