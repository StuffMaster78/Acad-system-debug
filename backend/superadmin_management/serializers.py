from rest_framework import serializers
from .models import SuperadminProfile, SuperadminLog
from django.contrib.auth import get_user_model
from superadmin_management.models import Probation  # Import at the top to avoid circular import

User = get_user_model()


### 🔹 1️⃣ Superadmin Profile Serializer (Includes Access Level Check)
class SuperadminProfileSerializer(serializers.ModelSerializer):
    """Serializer for Superadmin profile data."""
    has_full_access = serializers.SerializerMethodField()

    class Meta:
        model = SuperadminProfile
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]  # Prevent unwanted edits

    def get_has_full_access(self, obj):
        """Checks if Superadmin has all permissions enabled."""
        return all([
            obj.can_manage_users,
            obj.can_manage_payments,
            obj.can_view_reports,
            obj.can_modify_settings,
            obj.can_promote_users,
            obj.can_suspend_users,
            obj.can_blacklist_users,
            obj.can_resolve_disputes,
            obj.can_override_payments,
            obj.can_track_admins,
        ])


### 🔹 2️⃣ Superadmin Log Serializer (Formatted Timestamp)
class SuperadminLogSerializer(serializers.ModelSerializer):
    """Serializer for logging Superadmin actions."""
    superadmin = serializers.StringRelatedField()
    formatted_timestamp = serializers.SerializerMethodField()

    class Meta:
        model = SuperadminLog
        fields = "__all__"
        read_only_fields = ["superadmin", "action_type", "action_details", "timestamp"]  # Prevent edits

    def get_formatted_timestamp(self, obj):
        """Handles cases where `timestamp` might be `None`."""
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S") if obj.timestamp else None


### 🔹 3️⃣ User Serializer (Includes Probation Check)
class UserSerializer(serializers.ModelSerializer):
    """Serializer for user management by Superadmin."""
    is_on_probation = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "is_suspended", "date_joined", "is_on_probation"]
        read_only_fields = ["id", "email", "date_joined"]  # Prevent modification of ID & email

    def get_is_on_probation(self, obj):
        """Check if the user is currently on probation."""
        return Probation.objects.filter(user=obj, is_active=True).exists()