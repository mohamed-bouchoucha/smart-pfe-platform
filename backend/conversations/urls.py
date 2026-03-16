from django.urls import path
from . import views

urlpatterns = [
    path('', views.ConversationListCreateView.as_view(), name='conversation_list_create'),
    path('<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('<int:pk>/messages/', views.SendMessageView.as_view(), name='send_message'),
]
