"""
Serializers for express class inquiry file attachments.
"""
from rest_framework import serializers
from class_management.models import ExpressClassInquiryFile


class ExpressClassInquiryFileSerializer(serializers.ModelSerializer):
    """Serializer for express class inquiry files."""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    uploaded_by_email = serializers.CharField(source='uploaded_by.email', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = ExpressClassInquiryFile
        fields = [
            'id', 'website', 'express_class', 'uploaded_by',
            'uploaded_by_username', 'uploaded_by_email',
            'file', 'file_url', 'file_name', 'file_size', 'file_size_mb',
            'description', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by', 'file_name', 'file_size']
    
    def get_file_url(self, obj):
        """Get the file URL."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_size_mb(self, obj):
        """Get file size in MB."""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None
    
    def create(self, validated_data):
        """Create inquiry file with auto-set metadata."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploaded_by'] = request.user
        
        # Auto-set file_name and file_size
        file = validated_data.get('file')
        if file:
            validated_data['file_name'] = file.name
            validated_data['file_size'] = file.size
        
        return super().create(validated_data)
