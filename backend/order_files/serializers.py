from rest_framework import serializers
from .models import (
    OrderFile, FileDeletionRequest, ExternalFileLink, ExtraServiceFile, OrderFilesConfig, OrderFileCategory, FileDownloadLog
)

class OrderFileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    uploaded_by_username = serializers.SerializerMethodField()
    uploaded_by_email = serializers.SerializerMethodField()
    uploaded_by_role = serializers.SerializerMethodField()
    uploaded_by_id = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    is_final_file = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = OrderFile
        fields = "__all__"
    
    def get_uploaded_by_username(self, obj):
        return obj.uploaded_by.username if obj.uploaded_by else None
    
    def get_uploaded_by_email(self, obj):
        return obj.uploaded_by.email if obj.uploaded_by else None
    
    def get_uploaded_by_role(self, obj):
        return obj.uploaded_by.role if obj.uploaded_by else None
    
    def get_uploaded_by_id(self, obj):
        return obj.uploaded_by.id if obj.uploaded_by else None
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else "Uncategorized"
    
    def get_is_final_file(self, obj):
        return obj.category.is_final_draft if obj.category else False
    
    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1] if '/' in obj.file.name else obj.file.name
        return None
    
    def get_file_size(self, obj):
        try:
            if obj.file:
                return obj.file.size
        except Exception:
            pass
        return None

class FileDeletionRequestSerializer(serializers.ModelSerializer):
    requested_by = serializers.StringRelatedField()

    class Meta:
        model = FileDeletionRequest
        fields = "__all__"

class ExternalFileLinkSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    uploaded_by_username = serializers.SerializerMethodField()
    uploaded_by_email = serializers.SerializerMethodField()
    reviewed_by_username = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ExternalFileLink
        fields = "__all__"
    
    def get_uploaded_by_username(self, obj):
        return obj.uploaded_by.username if obj.uploaded_by else None
    
    def get_uploaded_by_email(self, obj):
        return obj.uploaded_by.email if obj.uploaded_by else None
    
    def get_reviewed_by_username(self, obj):
        return obj.reviewed_by.username if obj.reviewed_by else None
    
    def get_status_display(self, obj):
        return obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status

class ExtraServiceFileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()

    class Meta:
        model = ExtraServiceFile
        fields = "__all__"

class OrderFilesConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderFilesConfig
        fields = "__all__"

class OrderFileCategorySerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)

    class Meta:
        model = OrderFileCategory
        fields = "__all__"

class FileDownloadLogSerializer(serializers.ModelSerializer):
    """Serializer for File Download Logs"""
    file_name = serializers.CharField(source='file.file.name', read_only=True)
    file_id = serializers.IntegerField(source='file.id', read_only=True)
    order_id = serializers.IntegerField(source='file.order.id', read_only=True)
    order_title = serializers.CharField(source='file.order.title', read_only=True)
    downloaded_by_username = serializers.CharField(source='downloaded_by.username', read_only=True)
    downloaded_by_email = serializers.EmailField(source='downloaded_by.email', read_only=True)
    downloaded_by_role = serializers.CharField(source='downloaded_by.role', read_only=True)
    
    class Meta:
        model = FileDownloadLog
        fields = [
            'id',
            'website',
            'file',
            'file_id',
            'file_name',
            'order_id',
            'order_title',
            'downloaded_by',
            'downloaded_by_username',
            'downloaded_by_email',
            'downloaded_by_role',
            'downloaded_at',
        ]
        read_only_fields = ['id', 'downloaded_at']