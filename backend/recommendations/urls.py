from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'', views.RecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('admin/stats/', views.AdminStatsView.as_view(), name='admin_stats'),
    path('', include(router.urls)),
]
