from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')
router.register(r'', views.ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
]
