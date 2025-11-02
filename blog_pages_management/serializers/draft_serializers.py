"""
Serializers for draft, revision, preview, and edit lock features.
"""
from rest_framework import serializers
from ..models.draft_editing import (
    BlogPostRevision, BlogPostAutoSave, BlogPostEditLock, BlogPostPreview
)


class BlogPostRevisionSerializer(serializers.ModelSerializer):
    """Serializer for blog post revisions."""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = BlogPostRevision
        fields = [
            'id', 'blog', 'revision_number', 'title', 'content',
            'meta_title', 'meta_description', 'authors_data', 'tags_data',
            'category_id', 'created_by', 'created_by_username', 'created_at',
            'change_summary', 'is_current', 'revision_notes', 'revision_tags'
        ]
        read_only_fields = ['revision_number', 'created_at']


class BlogPostAutoSaveSerializer(serializers.ModelSerializer):
    """Serializer for blog post autosaves."""
    saved_by_username = serializers.CharField(source='saved_by.username', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPostAutoSave
        fields = [
            'id', 'blog', 'title', 'content', 'meta_title', 'meta_description',
            'authors_data', 'tags_data', 'category_id', 'saved_by',
            'saved_by_username', 'saved_at', 'is_recovered', 'time_ago'
        ]
        read_only_fields = ['saved_at', 'time_ago']
    
    def get_time_ago(self, obj):
        """Get human-readable time ago."""
        from django.utils import timezone
        delta = timezone.now() - obj.saved_at
        
        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"


class BlogPostEditLockSerializer(serializers.ModelSerializer):
    """Serializer for blog post edit locks."""
    locked_by_username = serializers.CharField(source='locked_by.username', read_only=True)
    is_expired = serializers.ReadOnlyField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPostEditLock
        fields = [
            'id', 'blog', 'locked_by', 'locked_by_username', 'locked_at',
            'expires_at', 'is_active', 'is_expired', 'time_remaining'
        ]
        read_only_fields = ['locked_at', 'is_expired']
    
    def get_time_remaining(self, obj):
        """Get time remaining until lock expires."""
        if not obj.is_active or obj.is_expired():
            return None
        
        from django.utils import timezone
        delta = obj.expires_at - timezone.now()
        
        if delta.total_seconds() < 0:
            return "Expired"
        
        minutes = int(delta.total_seconds() / 60)
        if minutes > 60:
            hours = minutes // 60
            return f"{hours}h {minutes % 60}m"
        return f"{minutes}m"


class BlogPostPreviewSerializer(serializers.ModelSerializer):
    """Serializer for blog post preview tokens."""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    preview_url = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()
    is_valid = serializers.ReadOnlyField()
    
    class Meta:
        model = BlogPostPreview
        fields = [
            'id', 'blog', 'token', 'created_by', 'created_by_username',
            'expires_at', 'is_active', 'view_count', 'created_at',
            'preview_url', 'is_expired', 'is_valid'
        ]
        read_only_fields = ['token', 'created_at', 'view_count', 'is_expired', 'is_valid']
    
    def get_preview_url(self, obj):
        """Generate preview URL."""
        if obj.token:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/blog/preview/{obj.token}/')
            return f'/blog/preview/{obj.token}/'
        return None

