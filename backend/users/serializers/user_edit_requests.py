"""
Serializers for User Edit Requests.
"""
from rest_framework import serializers
from users.models.user_edit_requests import UserEditRequest


class UserEditRequestSerializer(serializers.ModelSerializer):
    """Serializer for user edit requests."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    reviewed_by_email = serializers.CharField(source='reviewed_by.email', read_only=True, allow_null=True)
    changes_summary = serializers.SerializerMethodField()
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = UserEditRequest
        fields = [
            'id',
            'user',
            'user_email',
            'user_username',
            'user_full_name',
            'website',
            'website_name',
            'request_type',
            'field_changes',
            'reason',
            'status',
            'reviewed_by',
            'reviewed_by_email',
            'reviewed_at',
            'admin_notes',
            'created_at',
            'updated_at',
            'completed_at',
            'changes_summary',
        ]
        read_only_fields = [
            'id',
            'status',
            'reviewed_by',
            'reviewed_at',
            'completed_at',
            'created_at',
            'updated_at',
        ]
    
    def get_user_full_name(self, obj):
        """Get user's full name."""
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name or ''} {obj.user.last_name or ''}".strip()
        return obj.user.username
    
    def get_changes_summary(self, obj):
        """Get human-readable summary of changes."""
        return obj.get_changes_summary()


class CreateUserEditRequestSerializer(serializers.Serializer):
    """Serializer for creating edit requests."""
    
    field_changes = serializers.JSONField(
        help_text="Dictionary of field changes: {field_name: new_value}"
    )
    request_type = serializers.ChoiceField(
        choices=UserEditRequest.REQUEST_TYPE_CHOICES,
        default='profile_update',
        required=False
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Reason for the change request"
    )
    
    def validate_field_changes(self, value):
        """Validate field changes."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("field_changes must be a dictionary.")
        if not value:
            raise serializers.ValidationError("At least one field change is required.")
        return value

