from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AdminProfile, AdminActivityLog, BlacklistedUser

User = get_user_model()

class AdminProfileSerializer(serializers.ModelSerializer):
    """Serializer for Admin profile data."""
    
    user = serializers.StringRelatedField()  # Show username instead of just ID

    class Meta:
        model = AdminProfile
        fields = "__all__"

class AdminLogSerializer(serializers.ModelSerializer):
    """Serializer for Admin action logs."""
    
    admin = serializers.StringRelatedField()  # Display admin's username
    target_user = serializers.StringRelatedField()  # Display affected user's username
    order = serializers.StringRelatedField()  # Display order ID (if applicable)

    class Meta:
        model = AdminActivityLog
        fields = ["id", "admin", "target_user", "order", "action", "details", "timestamp"]

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user management by Admins."""
    
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "role", "is_suspended", "date_joined",
            "is_on_probation", "probation_reason", "probation_start_date", "probation_end_date"
        ]

class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for Admins to create new users."""
    
    role = serializers.ChoiceField(choices=[("writer", "Writer"), ("editor", "Editor"), ("support", "Support"), ("client", "Client")])
    email = serializers.EmailField(required=True, allow_blank=False)  # Ensure email is required
    password = serializers.CharField(write_only=True, min_length=8)  # Enforce strong password
    
    class Meta:
        model = User
        fields = ["username", "email", "role", "phone_number", "password"]

    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        """Create a user with hashed password."""
        password = validated_data.pop("password", None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class SuspendUserSerializer(serializers.Serializer):
    """Serializer for suspending a user."""
    
    user_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=255, required=False)

    def validate_user_id(self, value):
        """Ensure the user exists before suspending."""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found.")
        return value

class DashboardSerializer(serializers.Serializer):
    """Serializer for returning Admin dashboard statistics."""
    
    total_writers = serializers.IntegerField()
    total_editors = serializers.IntegerField()
    total_support = serializers.IntegerField()
    total_clients = serializers.IntegerField()
    active_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    recent_logs = serializers.ListField(child=serializers.CharField())



class BlacklistedUserSerializer(serializers.ModelSerializer):
    """Serializer for Blacklisted Users."""

    blacklisted_by = serializers.StringRelatedField()

    class Meta:
        model = BlacklistedUser
        fields = ["email", "blacklisted_by", "reason", "blacklisted_at"]
