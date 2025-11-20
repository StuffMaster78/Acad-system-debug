"""
Serializers for email management (mass emails, digests, broadcasts).
"""
from rest_framework import serializers
from mass_emails.models import EmailCampaign, EmailRecipient
from notifications_system.models.digest_notifications import NotificationDigest
from notifications_system.models.broadcast_notification import BroadcastNotification
from websites.models import Website
from django.contrib.auth import get_user_model

User = get_user_model()


class MassEmailListSerializer(serializers.ModelSerializer):
    """Enhanced list serializer for mass emails with website info."""
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    website = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'title', 'subject', 'status',
            'email_type', 'scheduled_time', 'sent_time',
            'website', 'website_name', 'website_domain',
            'created_by_username', 'created_at'
        ]


class EmailDigestSerializer(serializers.ModelSerializer):
    """Serializer for email digests."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    
    class Meta:
        model = NotificationDigest
        fields = [
            'id', 'user', 'user_email', 'user_username',
            'website', 'website_name', 'website_domain',
            'event_key', 'digest_group', 'event',
            'scheduled_for', 'is_sent', 'sent_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'sent_at']


class EmailDigestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating email digests."""
    
    class Meta:
        model = NotificationDigest
        fields = [
            'user', 'website', 'event_key', 'digest_group',
            'event', 'scheduled_for', 'payload',
        ]
    
    def create(self, validated_data):
        # Set default values
        validated_data.setdefault('is_sent', False)
        return super().create(validated_data)


class BroadcastMessageSerializer(serializers.ModelSerializer):
    """Serializer for broadcast messages."""
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = BroadcastNotification
        fields = [
            'id', 'title', 'message', 'event_type',
            'website', 'website_name', 'website_domain',
            'target_roles', 'channels',
            'is_active', 'is_blocking', 'require_acknowledgement',
            'pinned', 'dismissible', 'send_email', 'show_in_dashboard',
            'scheduled_for', 'sent_at', 'expires_at',
            'created_by', 'created_by_email', 'created_by_username',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'sent_at', 'created_by']


class BroadcastMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating broadcast messages."""
    
    class Meta:
        model = BroadcastNotification
        fields = [
            'title', 'message', 'event_type',
            'website', 'target_roles', 'channels',
            'is_active', 'is_blocking', 'require_acknowledgement',
            'pinned', 'dismissible', 'send_email', 'show_in_dashboard',
            'scheduled_for', 'expires_at',
        ]
    
    def validate_channels(self, value):
        """Validate channels."""
        valid_channels = ['in_app', 'email', 'sms', 'push']
        if value:
            for channel in value:
                if channel not in valid_channels:
                    raise serializers.ValidationError(f"Invalid channel: {channel}")
        return value

