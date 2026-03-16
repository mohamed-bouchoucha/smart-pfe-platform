from django.db import models
from django.conf import settings


class Document(models.Model):
    """User-uploaded document (CV, cahier des charges, report)."""

    class DocType(models.TextChoices):
        CV = 'cv', 'CV'
        CAHIER_CHARGES = 'cahier_charges', 'Cahier des charges'
        REPORT = 'report', 'Rapport'
        OTHER = 'other', 'Autre'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/%Y/%m/')
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    file_size = models.IntegerField(default=0, help_text="Size in bytes")
    mime_type = models.CharField(max_length=100, blank=True)
    extracted_text = models.TextField(blank=True)
    is_analyzed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documents'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} ({self.get_doc_type_display()})"
