"""
Privacy-aware serializers that mask personal information based on viewer role.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from writer_management.models.profile import WriterProfile
from client_management.models import ClientProfile

User = get_user_model()


class PrivacyAwareWriterSerializer(serializers.ModelSerializer):
    """
    Serializer for writers that masks personal info when viewed by clients.
    Shows pen_name or registration_id instead of real name/email.
    """
    display_name = serializers.SerializerMethodField()
    registration_id = serializers.CharField(source='writer_profile.registration_id', read_only=True)
    pen_name = serializers.CharField(source='writer_profile.pen_name', read_only=True)
    is_online = serializers.SerializerMethodField()
    timezone = serializers.CharField(source='writer_profile.timezone', read_only=True)
    is_daytime = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'display_name', 'registration_id', 'pen_name',
            'is_online', 'timezone', 'is_daytime'
        ]
    
    def get_display_name(self, obj):
        """Return pen_name if set, otherwise registration_id"""
        if hasattr(obj, 'writer_profile'):
            if obj.writer_profile.pen_name:
                return obj.writer_profile.pen_name
            return obj.writer_profile.registration_id
        return f"Writer #{obj.id}"
    
    def get_is_online(self, obj):
        """Check if writer is online (active within last 5 minutes)"""
        from django.utils.timezone import now
        from datetime import timedelta
        
        if hasattr(obj, 'writer_profile') and obj.writer_profile.last_active:
            online_threshold = now() - timedelta(minutes=5)
            return obj.writer_profile.last_active >= online_threshold
        return False
    
    def get_is_daytime(self, obj):
        """Check if it's daytime in writer's timezone"""
        from django.utils.timezone import now
        import pytz
        
        if hasattr(obj, 'writer_profile'):
            timezone_str = obj.writer_profile.timezone or "UTC"
            try:
                tz = pytz.timezone(timezone_str)
                local_time = now().astimezone(tz)
                hour = local_time.hour
                return 6 <= hour < 20  # Daytime: 6 AM to 8 PM
            except Exception:
                return True
        return True


class PrivacyAwareClientSerializer(serializers.ModelSerializer):
    """
    Serializer for clients that masks personal info when viewed by writers.
    Shows registration_id instead of real name/email.
    """
    display_name = serializers.SerializerMethodField()
    registration_id = serializers.CharField(source='client_profile.registration_id', read_only=True)
    is_online = serializers.SerializerMethodField()
    timezone = serializers.CharField(source='client_profile.timezone', read_only=True)
    is_daytime = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'display_name', 'registration_id',
            'is_online', 'timezone', 'is_daytime'
        ]
    
    def get_display_name(self, obj):
        """Return registration_id as display name"""
        if hasattr(obj, 'client_profile'):
            return obj.client_profile.registration_id
        return f"Client #{obj.id}"
    
    def get_is_online(self, obj):
        """Check if client is online (active within last 5 minutes)"""
        from django.utils.timezone import now
        from datetime import timedelta
        
        if hasattr(obj, 'client_profile') and obj.client_profile.last_online:
            online_threshold = now() - timedelta(minutes=5)
            return obj.client_profile.last_online >= online_threshold
        return False
    
    def get_is_daytime(self, obj):
        """Check if it's daytime in client's timezone"""
        from django.utils.timezone import now
        import pytz
        
        if hasattr(obj, 'client_profile'):
            timezone_str = obj.client_profile.timezone or "UTC"
            try:
                tz = pytz.timezone(timezone_str)
                local_time = now().astimezone(tz)
                hour = local_time.hour
                return 6 <= hour < 20  # Daytime: 6 AM to 8 PM
            except Exception:
                return True
        return True


def get_privacy_aware_serializer(user_role, target_role, request_user=None):
    """
    Get the appropriate privacy-aware serializer based on roles.
    
    Args:
        user_role: Role of the user being serialized
        target_role: Role of the user viewing the data
        request_user: The user making the request (for admin checks)
    
    Returns:
        Serializer class appropriate for the privacy context
    """
    # Admins and superadmins see everything
    if request_user and (request_user.is_staff or request_user.role in ['admin', 'superadmin']):
        return None  # Use regular serializer
    
    # Writers viewing clients: use privacy-aware client serializer
    if user_role == 'client' and target_role == 'writer':
        return PrivacyAwareClientSerializer
    
    # Clients viewing writers: use privacy-aware writer serializer
    if user_role == 'writer' and target_role == 'client':
        return PrivacyAwareWriterSerializer
    
    # Default: no privacy masking needed (same role or admin)
    return None

