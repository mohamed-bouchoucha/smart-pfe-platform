import os
from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id', 'filename', 'file', 'doc_type', 'project', 'file_size',
            'mime_type', 'is_analyzed', 'uploaded_at',
        ]
        read_only_fields = ['id', 'filename', 'file_size', 'mime_type', 'is_analyzed', 'uploaded_at']


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['file', 'doc_type', 'project']

    def validate_file(self, value):
        # 5 MB max size limit
        max_size = 5 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("La taille du fichier ne doit pas dépasser 5 Mo.")
        
        # Extension validation
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg']
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f"Type de fichier non supporté. Les types autorisés sont : {', '.join(valid_extensions)}"
            )

        return value

    def create(self, validated_data):
        file_obj = validated_data['file']
        validated_data['filename'] = file_obj.name
        validated_data['file_size'] = file_obj.size
        validated_data['mime_type'] = getattr(file_obj, 'content_type', '')
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
