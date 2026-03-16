from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'user', 'doc_type', 'file_size', 'is_analyzed', 'uploaded_at']
    list_filter = ['doc_type', 'is_analyzed', 'uploaded_at']
    search_fields = ['filename', 'user__username']
