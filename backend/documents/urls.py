from django.urls import path
from . import views

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('upload/', views.DocumentUploadView.as_view(), name='document_upload'),
    path('<int:pk>/', views.DocumentDeleteView.as_view(), name='document_delete'),
]
