from rest_framework import serializers


class ActivateAccountSerializer(serializers.Serializer):
    """Serializer for account activation requests."""

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="Account activated.",
    )
    metadata = serializers.JSONField(required=False)


class SuspendAccountSerializer(serializers.Serializer):
    """Serializer for account suspension requests."""

    reason = serializers.CharField(required=True, allow_blank=False)
    metadata = serializers.JSONField(required=False)


class ReactivateAccountSerializer(serializers.Serializer):
    """Serializer for account reactivation requests."""

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="Account reactivated.",
    )
    metadata = serializers.JSONField(required=False)