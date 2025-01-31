from rest_framework import serializers
from .models import SuperadminProfile, SuperadminLog
from django.contrib.auth import get_user_model

User = get_user_model()

class SuperadminProfileSerializer(serializers.ModelSerializer):
    """Serializer for Superadmin profile data."""
    class Meta:
        model = SuperadminProfile
        fields = "__all__"

class SuperadminLogSerializer(serializers.ModelSerializer):
    """Serializer for logging Superadmin actions."""
    superadmin = serializers.StringRelatedField()

    class Meta:
        model = SuperadminLog
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user management by Superadmin."""
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "is_suspended", "date_joined"]