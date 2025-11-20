"""
Serializers for PDF sample sections and downloads.
"""
from rest_framework import serializers
from ..models.pdf_samples import (
    PDFSampleSection, PDFSample, PDFSampleDownload
)


class PDFSampleSerializer(serializers.ModelSerializer):
    """Serializer for individual PDF samples."""
    file_size_human = serializers.ReadOnlyField()
    file_url = serializers.SerializerMethodField()
    download_count = serializers.ReadOnlyField()
    
    class Meta:
        model = PDFSample
        fields = [
            'id', 'section', 'title', 'description', 'pdf_file',
            'file_size', 'file_size_human', 'file_url', 'display_order',
            'download_count', 'is_featured', 'is_active', 'uploaded_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['file_size', 'download_count', 'uploaded_by', 'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        """Get download URL for the PDF file."""
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None


class PDFSampleSectionSerializer(serializers.ModelSerializer):
    """Serializer for PDF sample sections."""
    pdf_samples = PDFSampleSerializer(many=True, read_only=True)
    pdf_samples_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PDFSampleSection
        fields = [
            'id', 'blog', 'title', 'description', 'display_order',
            'is_active', 'requires_auth', 'pdf_samples', 'pdf_samples_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_pdf_samples_count(self, obj):
        """Get count of active PDF samples in this section."""
        return obj.pdf_samples.filter(is_active=True).count()


class PDFSampleDownloadSerializer(serializers.ModelSerializer):
    """Serializer for PDF download tracking."""
    pdf_sample_title = serializers.CharField(source='pdf_sample.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = PDFSampleDownload
        fields = [
            'id', 'pdf_sample', 'pdf_sample_title', 'user', 'user_username',
            'ip_address', 'user_agent', 'session_id', 'downloaded_at'
        ]
        read_only_fields = ['downloaded_at']

