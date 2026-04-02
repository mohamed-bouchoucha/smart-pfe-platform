from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.ConversationViewSet, basename='conversation')

urlpatterns = [
    path('', include(router.urls)),
]
