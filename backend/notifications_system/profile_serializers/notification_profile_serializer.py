"""
Serializers for notification preference profiles.
"""
from rest_framework import serializers
from notifications_system.models.notification_preferences import NotificationPreferenceProfile
from websites.models import Website


class NotificationProfileSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreferenceProfile."""
    
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_id = serializers.IntegerField(source='website.id', read_only=True)
    
    class Meta:
        model = NotificationPreferenceProfile
        fields = [
            'id',
            'name',
            'description',
            'website',
            'website_id',
            'website_name',
            'default_email',
            'default_sms',
            'default_push',
            'default_in_app',
            'email_enabled',
            'sms_enabled',
            'push_enabled',
            'in_app_enabled',
            'dnd_enabled',
            'dnd_start_hour',
            'dnd_end_hour',
            'is_default',
        ]
        read_only_fields = ['id']
    
    def validate_dnd_start_hour(self, value):
        """Validate DND start hour is between 0-23."""
        if value < 0 or value > 23:
            raise serializers.ValidationError("DND start hour must be between 0 and 23")
        return value
    
    def validate_dnd_end_hour(self, value):
        """Validate DND end hour is between 0-23."""
        if value < 0 or value > 23:
            raise serializers.ValidationError("DND end hour must be between 0 and 23")
        return value
    
    def validate_name(self, value):
        """Validate profile name is unique."""
        if self.instance:
            # Update: check uniqueness excluding current instance
            if NotificationPreferenceProfile.objects.filter(
                name=value
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("A profile with this name already exists")
        else:
            # Create: check uniqueness
            if NotificationPreferenceProfile.objects.filter(name=value).exists():
                raise serializers.ValidationError("A profile with this name already exists")
        return value


class NotificationProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notification profiles."""
    
    class Meta:
        model = NotificationPreferenceProfile
        fields = [
            'name',
            'description',
            'website',
            'default_email',
            'default_sms',
            'default_push',
            'default_in_app',
            'email_enabled',
            'sms_enabled',
            'push_enabled',
            'in_app_enabled',
            'dnd_enabled',
            'dnd_start_hour',
            'dnd_end_hour',
            'is_default',
        ]
    
    def validate_dnd_start_hour(self, value):
        """Validate DND start hour is between 0-23."""
        if value < 0 or value > 23:
            raise serializers.ValidationError("DND start hour must be between 0 and 23")
        return value
    
    def validate_dnd_end_hour(self, value):
        """Validate DND end hour is between 0-23."""
        if value < 0 or value > 23:
            raise serializers.ValidationError("DND end hour must be between 0 and 23")
        return value


class ApplyProfileSerializer(serializers.Serializer):
    """Serializer for applying a profile to users."""
    
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of user IDs to apply profile to. If not provided, applies to current user."
    )
    override_existing = serializers.BooleanField(
        default=False,
        help_text="Whether to override existing user preferences"
    )


class DuplicateProfileSerializer(serializers.Serializer):
    """Serializer for duplicating a profile."""
    
    new_name = serializers.CharField(
        max_length=100,
        help_text="Name for the duplicated profile"
    )
    website = serializers.PrimaryKeyRelatedField(
        queryset=Website.objects.all(),
        required=False,
        allow_null=True,
        help_text="Website for the new profile (uses source profile's website if not provided)"
    )

