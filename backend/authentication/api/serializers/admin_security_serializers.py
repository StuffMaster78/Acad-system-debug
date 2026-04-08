from rest_framework import serializers


class AdminUnlockResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    user_id = serializers.IntegerField()
    message = serializers.CharField()


class AdminKickoutSerializer(serializers.Serializer):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class AdminKickoutResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    user_id = serializers.IntegerField()
    revoked_sessions_count = serializers.IntegerField()
    message = serializers.CharField()