from rest_framework import serializers
from .models import (
    OrderFile, FileDeletionRequest, ExternalFileLink, ExtraServiceFile, OrderFilesConfig, OrderFileCategory
)

class OrderFileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    uploaded_by_username = serializers.SerializerMethodField()
    uploaded_by_email = serializers.SerializerMethodField()
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
    class Meta:
        model = OrderFileCategory
        fields = "__all__"