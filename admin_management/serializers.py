from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AdminProfile, AdminLog

User = get_user_model()

class AdminProfileSerializer(serializers.ModelSerializer):
    """Serializer for Admin profile data."""
    
    class Meta:
        model = AdminProfile
        fields = "__all__"

class AdminLogSerializer(serializers.ModelSerializer):
    """Serializer for Admin action logs."""
    admin = serializers.StringRelatedField()

    class Meta:
        model = AdminLog
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user management by Admins."""
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "is_suspended", "date_joined"]

class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for Admins to create new users."""
    role = serializers.ChoiceField(choices=[("writer", "Writer"), ("editor", "Editor"), ("support", "Support"), ("client", "Client")])

    class Meta:
        model = User
        fields = ["username", "email", "role", "phone_number"]

class SuspendUserSerializer(serializers.Serializer):
    """Serializer for suspending a user."""
    user_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=255, required=False)

class DashboardSerializer(serializers.Serializer):
    """Serializer for returning Admin dashboard statistics."""
    total_writers = serializers.IntegerField()
    total_editors = serializers.IntegerField()
    total_support = serializers.IntegerField()
    recent_logs = serializers.ListField(child=serializers.CharField())