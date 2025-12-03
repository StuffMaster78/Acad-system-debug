"""
Serializers for profile change requests and avatar uploads.
"""
from rest_framework import serializers
from users.models.profile_changes import ProfileChangeRequest, WriterAvatarUpload


class ProfileChangeRequestSerializer(serializers.ModelSerializer):
    """Serializer for profile change requests."""
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    approved_by_email = serializers.CharField(source='approved_by.email', read_only=True, allow_null=True)
    
    class Meta:
        model = ProfileChangeRequest
        fields = [
            'id', 'user', 'user_email', 'change_type', 'change_type_display',
            'current_value', 'requested_value', 'status', 'status_display',
            'approved_by', 'approved_by_email', 'approved_at', 'rejection_reason',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'approved_at', 'completed_at'
        ]


class WriterAvatarUploadSerializer(serializers.ModelSerializer):
    """Serializer for writer avatar uploads."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    approved_by_email = serializers.CharField(source='approved_by.email', read_only=True, allow_null=True)
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = WriterAvatarUpload
        fields = [
            'id', 'user', 'user_email', 'avatar_file', 'avatar_url',
            'status', 'status_display', 'approved_by', 'approved_by_email',
            'approved_at', 'rejection_reason', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'approved_by', 'approved_at', 'created_at'
        ]
    
    def get_avatar_url(self, obj):
        """Get avatar URL."""
        if obj.avatar_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar_file.url)
            return obj.avatar_file.url
        return None

