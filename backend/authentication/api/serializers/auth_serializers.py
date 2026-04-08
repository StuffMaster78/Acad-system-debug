from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    fingerprint_data = serializers.JSONField(required=False)
    device_name = serializers.CharField(required=False, allow_blank=True)


class LoginResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    session_id = serializers.IntegerField(required=False)
    mfa_required = serializers.BooleanField()
    user_id = serializers.IntegerField(required=False)