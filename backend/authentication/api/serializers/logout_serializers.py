from rest_framework import serializers


class LogoutResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


class LogoutAllOthersResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    revoked_sessions_count = serializers.IntegerField()
    message = serializers.CharField()