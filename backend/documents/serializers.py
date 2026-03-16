from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id', 'filename', 'file', 'doc_type', 'file_size',
            'mime_type', 'is_analyzed', 'uploaded_at',
        ]
        read_only_fields = ['id', 'filename', 'file_size', 'mime_type', 'is_analyzed', 'uploaded_at']


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['file', 'doc_type']

    def create(self, validated_data):
        file_obj = validated_data['file']
        validated_data['filename'] = file_obj.name
        validated_data['file_size'] = file_obj.size
        validated_data['mime_type'] = getattr(file_obj, 'content_type', '')
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
