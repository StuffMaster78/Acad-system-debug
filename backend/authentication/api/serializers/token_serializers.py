from rest_framework import serializers


class SecureTokenSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    purpose = serializers.CharField()
    expires_at = serializers.DateTimeField()
    is_active = serializers.BooleanField()