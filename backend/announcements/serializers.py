"""
Serializers for announcements app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from notifications_system.models.broadcast_notification import BroadcastNotification
from notifications_system.serializers import BroadcastNotificationSerializer
from .models import Announcement, AnnouncementView

User = get_user_model()


class AnnouncementViewSerializer(serializers.ModelSerializer):
    """Serializer for AnnouncementView."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = AnnouncementView
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'viewed_at', 'time_spent', 'acknowledged', 'acknowledged_at'
        ]
        read_only_fields = ['id', 'viewed_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    """Serializer for Announcement (public view)."""
    # Fields from linked broadcast
    title = serializers.CharField(source='broadcast.title', read_only=True)
    message = serializers.CharField(source='broadcast.message', read_only=True)
    is_pinned = serializers.BooleanField(source='broadcast.pinned', read_only=True)
    is_active = serializers.BooleanField(source='broadcast.is_active', read_only=True)
    website_id = serializers.IntegerField(source='broadcast.website.id', read_only=True)
    website_name = serializers.CharField(source='broadcast.website.name', read_only=True)
    target_roles = serializers.ListField(source='broadcast.target_roles', read_only=True)
    created_at = serializers.DateTimeField(source='broadcast.created_at', read_only=True)
    expires_at = serializers.DateTimeField(source='broadcast.expires_at', read_only=True)
    created_by_name = serializers.CharField(
        source='broadcast.created_by.get_full_name',
        read_only=True
    )

    # User-specific fields
    is_read = serializers.SerializerMethodField()
    is_acknowledged = serializers.SerializerMethodField()
    viewed_at = serializers.SerializerMethodField()

    # Featured image URL
    featured_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'message', 'category', 'featured_image_url',
            'read_more_url', 'is_pinned', 'is_active', 'website_id',
            'website_name', 'target_roles', 'view_count', 'created_at',
            'expires_at', 'created_by_name', 'is_read', 'is_acknowledged',
            'viewed_at'
        ]
        read_only_fields = ['id', 'view_count']

    def get_is_read(self, obj):
        """Check if current user has read this announcement."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Use prefetched user_views if available (optimized)
            if hasattr(obj, 'user_views') and obj.user_views:
                return True
            # Fallback to direct query if prefetch not available
            return AnnouncementView.objects.filter(
                user=request.user,
                announcement=obj
            ).exists()
        return False

    def get_is_acknowledged(self, obj):
        """Check if current user has acknowledged this announcement."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Use prefetched user_views if available (optimized)
            if hasattr(obj, 'user_views') and obj.user_views:
                return obj.user_views[0].acknowledged if obj.user_views else False
            # Fallback to direct query if prefetch not available
            view = AnnouncementView.objects.filter(
                user=request.user,
                announcement=obj
            ).first()
            return view.acknowledged if view else False
        return False

    def get_viewed_at(self, obj):
        """Get when current user viewed this announcement."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Use prefetched user_views if available (optimized)
            if hasattr(obj, 'user_views') and obj.user_views:
                return obj.user_views[0].viewed_at if obj.user_views else None
            # Fallback to direct query if prefetch not available
            view = AnnouncementView.objects.filter(
                user=request.user,
                announcement=obj
            ).first()
            return view.viewed_at if view else None
        return None

    def get_featured_image_url(self, obj):
        """Get featured image URL."""
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating announcements."""
    title = serializers.CharField(write_only=True)
    message = serializers.CharField(write_only=True)
    target_roles = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        default=list
    )
    channels = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        default=['in_app', 'email']
    )
    pinned = serializers.BooleanField(write_only=True, required=False, default=False)
    require_acknowledgement = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False
    )
    expires_at = serializers.DateTimeField(write_only=True, required=False, allow_null=True)
    scheduled_for = serializers.DateTimeField(write_only=True, required=False, allow_null=True)
    website_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Announcement
        fields = [
            'title', 'message', 'category', 'featured_image',
            'read_more_url', 'target_roles', 'channels', 'pinned',
            'require_acknowledgement', 'expires_at', 'scheduled_for', 'website_id'
        ]

    def create(self, validated_data):
        """Create announcement with linked broadcast."""
        from notifications_system.services.broadcast_services import BroadcastNotificationService

        # Extract broadcast fields
        title = validated_data.pop('title')
        message = validated_data.pop('message')
        target_roles = validated_data.pop('target_roles', [])
        channels = validated_data.pop('channels', ['in_app', 'email'])
        pinned = validated_data.pop('pinned', False)
        require_acknowledgement = validated_data.pop('require_acknowledgement', False)
        expires_at = validated_data.pop('expires_at', None)
        scheduled_for = validated_data.pop('scheduled_for', None)
        website_id = validated_data.pop('website_id', None)

        # Get website
        request = self.context.get('request')
        if website_id:
            from websites.models import Website
            website = Website.objects.get(id=website_id)
        else:
            website = getattr(request.user, 'website', None)

        # Create broadcast notification
        broadcast = BroadcastNotification.objects.create(
            title=title,
            message=message,
            event_type='broadcast.system_announcement',
            website=website,
            target_roles=target_roles,
            channels=channels,
            pinned=pinned,
            require_acknowledgement=require_acknowledgement,
            expires_at=expires_at,
            scheduled_for=scheduled_for,
            is_active=True,
            created_by=request.user if request else None
        )

        # Send immediately if not scheduled
        if not scheduled_for:
            from notifications_system.services.broadcast_services import BroadcastNotificationService
            BroadcastNotificationService.send_broadcast(
                event=broadcast.event_type,
                title=broadcast.title,
                message=broadcast.message,
                website=broadcast.website,
                channels=broadcast.channels or ['in_app', 'email'],
                is_test=False
            )
            broadcast.sent_at = timezone.now()
            broadcast.save(update_fields=['sent_at'])

        # Create announcement
        announcement = Announcement.objects.create(
            broadcast=broadcast,
            category=validated_data.get('category', 'general'),
            featured_image=validated_data.get('featured_image'),
            read_more_url=validated_data.get('read_more_url')
        )

        return announcement


class AnnouncementUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating announcements."""
    title = serializers.CharField(required=False, write_only=True)
    message = serializers.CharField(required=False, write_only=True)
    pinned = serializers.BooleanField(required=False, write_only=True)
    is_active = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Announcement
        fields = [
            'category', 'featured_image', 'read_more_url',
            'title', 'message', 'pinned', 'is_active'
        ]

    def update(self, instance, validated_data):
        """Update announcement and linked broadcast."""
        # Update broadcast fields if provided
        if 'title' in validated_data:
            instance.broadcast.title = validated_data.pop('title')
        if 'message' in validated_data:
            instance.broadcast.message = validated_data.pop('message')
        if 'pinned' in validated_data:
            instance.broadcast.pinned = validated_data.pop('pinned')
        if 'is_active' in validated_data:
            instance.broadcast.is_active = validated_data.pop('is_active')

        instance.broadcast.save()

        # Update announcement fields
        return super().update(instance, validated_data)


class AnnouncementAnalyticsSerializer(serializers.Serializer):
    """Serializer for announcement analytics."""
    total_views = serializers.IntegerField()
    unique_viewers = serializers.IntegerField()
    acknowledged_count = serializers.IntegerField()
    engagement_rate = serializers.FloatField()
    views_by_role = serializers.DictField()
    views_over_time = serializers.ListField(
        child=serializers.DictField()
    )
    readers = serializers.ListField(
        child=AnnouncementViewSerializer()
    )
    non_readers_count = serializers.IntegerField()

