from rest_framework import serializers


class SessionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ip_address = serializers.CharField(allow_null=True)
    user_agent = serializers.CharField()
    device_name = serializers.CharField(allow_null=True)
    logged_in_at = serializers.DateTimeField()
    is_active = serializers.BooleanField()


class RevokeSessionSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()


class RevokeAllSessionsSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()


class CurrentSessionResponseSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    session_type = serializers.CharField()
    ip_address = serializers.CharField(
        allow_null=True,
        required=False,
    )
    user_agent = serializers.CharField(
        allow_null=True,
        required=False,
    )
    device_name = serializers.CharField(
        allow_null=True,
        required=False,
    )
    fingerprint_hash = serializers.CharField(
        allow_null=True,
        required=False,
    )
    logged_in_at = serializers.DateTimeField()
    last_activity_at = serializers.DateTimeField(
        allow_null=True,
        required=False,
    )
    expires_at = serializers.DateTimeField(
        allow_null=True,
        required=False,
    )
    is_active = serializers.BooleanField()
    idle_timeout_seconds = serializers.IntegerField()
    idle_remaining_seconds = serializers.IntegerField()
    warning_time_seconds = serializers.IntegerField()


class ExtendSessionResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    session_id = serializers.IntegerField()
    idle_timeout_seconds = serializers.IntegerField()
    idle_remaining_seconds = serializers.IntegerField()
    message = serializers.CharField()