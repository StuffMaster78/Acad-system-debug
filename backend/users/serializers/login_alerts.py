"""
Login Alert Preferences Serializers
"""
from rest_framework import serializers
from users.login_alerts import LoginAlertPreference


class LoginAlertPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for login alert preferences."""
    
    class Meta:
        model = LoginAlertPreference
        fields = [
            'id',
            'user',
            'website',
            'notify_new_login',
            'notify_new_device',
            'notify_new_location',
            'email_enabled',
            'push_enabled',
            'in_app_enabled',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'website', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create preference for the current user and website."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
            validated_data['website'] = request.user.website
        return super().create(validated_data)


class LoginAlertPreferenceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating login alert preferences."""
    
    class Meta:
        model = LoginAlertPreference
        fields = [
            'notify_new_login',
            'notify_new_device',
            'notify_new_location',
            'email_enabled',
            'push_enabled',
            'in_app_enabled',
        ]

