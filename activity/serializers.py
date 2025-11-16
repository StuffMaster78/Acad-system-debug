from rest_framework import serializers
from activity.models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for activity logs with expanded context."""
    user = serializers.StringRelatedField()
    triggered_by = serializers.StringRelatedField()
    user_role = serializers.SerializerMethodField()
    website = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "user",
            "user_role",
            "triggered_by",
            "website",
            "actor_type",
            "action_type",
            "action_subtype",
            "description",
            "timestamp",
            "metadata",
        ]
        read_only_fields = ["id", "timestamp", "metadata"]

    def get_user_role(self, obj):
        """Get the role of the user associated with the activity log."""
        try:
            if not obj.user:
                return None
            # Check if user has a role attribute directly
            if hasattr(obj.user, "role"):
                return obj.user.role
            # Check if user has a profile with role
            if hasattr(obj.user, "profile"):
                return getattr(obj.user.profile, "role", None)
            return getattr(obj.user, "user_type", None)
        except Exception:
            return None
    
    def get_website(self, obj):
        """Get website information."""
        try:
            if obj.website:
                return {
                    "id": obj.website.id,
                    "name": obj.website.name,
                    "domain": obj.website.domain,
                    "slug": obj.website.slug if hasattr(obj.website, "slug") else None,
                }
        except Exception:
            pass
        return None