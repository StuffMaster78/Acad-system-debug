"""
Serializers for Website Integration Configurations
"""
from rest_framework import serializers
from .models_integrations import WebsiteIntegrationConfig


class WebsiteIntegrationConfigSerializer(serializers.ModelSerializer):
    """Serializer for WebsiteIntegrationConfig (read-only for sensitive fields)."""
    
    # These fields are read-only in the API to prevent accidental exposure
    api_key = serializers.SerializerMethodField(read_only=True)
    secret_key = serializers.SerializerMethodField(read_only=True)
    access_token = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = WebsiteIntegrationConfig
        fields = [
            'id', 'website', 'integration_type', 'is_active',
            'api_key', 'secret_key', 'access_token',
            'config', 'name', 'description',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_api_key(self, obj):
        """Return masked API key (only show last 4 characters)."""
        try:
            key = obj.get_api_key()
            if key and len(key) > 4:
                return '*' * (len(key) - 4) + key[-4:]
            return '****' if key else None
        except Exception:
            return None
    
    def get_secret_key(self, obj):
        """Return masked secret key (only show last 4 characters)."""
        try:
            key = obj.get_secret_key()
            if key and len(key) > 4:
                return '*' * (len(key) - 4) + key[-4:]
            return '****' if key else None
        except Exception:
            return None
    
    def get_access_token(self, obj):
        """Return masked access token (only show last 4 characters)."""
        try:
            token = obj.get_access_token()
            if token and len(token) > 4:
                return '*' * (len(key) - 4) + token[-4:]
            return '****' if token else None
        except Exception:
            return None


class WebsiteIntegrationConfigCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating integration configs (accepts plain text keys)."""
    
    api_key = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="API key (will be encrypted before saving)"
    )
    secret_key = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Secret key (will be encrypted before saving)"
    )
    access_token = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Access token (will be encrypted before saving)"
    )
    
    class Meta:
        model = WebsiteIntegrationConfig
        fields = [
            'id', 'website', 'integration_type', 'is_active',
            'api_key', 'secret_key', 'access_token',
            'config', 'name', 'description'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """Create integration config with encrypted keys."""
        api_key = validated_data.pop('api_key', None)
        secret_key = validated_data.pop('secret_key', None)
        access_token = validated_data.pop('access_token', None)
        
        # Get user from request context
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        
        instance = WebsiteIntegrationConfig(**validated_data)
        
        # Set encrypted keys
        if api_key:
            instance.set_api_key(api_key)
        if secret_key:
            instance.set_secret_key(secret_key)
        if access_token:
            instance.set_access_token(access_token)
        
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        """Update integration config with encrypted keys."""
        api_key = validated_data.pop('api_key', None)
        secret_key = validated_data.pop('secret_key', None)
        access_token = validated_data.pop('access_token', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update encrypted keys if provided
        if api_key is not None:
            instance.set_api_key(api_key if api_key else "")
        if secret_key is not None:
            instance.set_secret_key(secret_key if secret_key else "")
        if access_token is not None:
            instance.set_access_token(access_token if access_token else "")
        
        instance.save()
        return instance

