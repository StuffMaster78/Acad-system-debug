"""
Serializers for account management operations.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    
    def validate_new_password(self, value):
        """Validate new password with Django's validators."""
        validate_password(value)
        return value


class CompletePasswordResetSerializer(serializers.Serializer):
    """
    Serializer to complete password reset using token and OTP.
    """
    token = serializers.CharField(max_length=255, required=True)
    otp_code = serializers.CharField(max_length=6, min_length=6, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    
    def validate_new_password(self, value):
        """Validate new password with Django's validators."""
        validate_password(value)
        return value
    
    def validate_otp_code(self, value):
        """Validate OTP code is numeric."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must be numeric.")
        return value


class ProfileUpdateRequestSerializer(serializers.Serializer):
    """Serializer for profile update requests."""
    requested_data = serializers.DictField(required=True)
    
    def validate_requested_data(self, value):
        """Validate that requested data contains valid fields."""
        allowed_fields = [
            'email', 'username', 'first_name', 'last_name',
            'phone_number', 'bio', 'country', 'state', 'website', 'role'
        ]
        
        invalid_fields = [field for field in value.keys() if field not in allowed_fields]
        if invalid_fields:
            raise serializers.ValidationError(
                f"Invalid fields: {', '.join(invalid_fields)}"
            )
        
        return value


class AccountDeletionRequestSerializer(serializers.Serializer):
    """Serializer for account deletion requests."""
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)

