from rest_framework import serializers
from activity.models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for activity logs with expanded context."""
    user = serializers.StringRelatedField()
    triggered_by = serializers.StringRelatedField()
    user_role = serializers.SerializerMethodField()
    website = serializers.SlugRelatedField(
        slug_field="slug",
        read_only=True
    )
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "user",
            "user_role",
            "triggered_by",
            "website",
            "action_type",
            "description",
            "timestamp",
            "metadata",
        ]
        read_only_fields = ["id", "timestamp", "metadata"]

    def get_user_role(self, obj):
        """Get the role of the user associated with the activity log."""
        # Assuming user has a profile with a role attribute
        # or a user_type attribute directly on the user model
        if not obj.user:
            return None # Handle case where user is None    
        if hasattr(obj.user, "profile"):
            return getattr(obj.user.profile, "role", None)
        return getattr(obj.user, "user_type", None)  # fallback