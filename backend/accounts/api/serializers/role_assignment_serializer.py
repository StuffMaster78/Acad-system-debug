from rest_framework import serializers


class AssignRoleSerializer(serializers.Serializer):
    """Serializer for role assignment requests."""

    role_key = serializers.CharField()
    metadata = serializers.JSONField(required=False)


class RevokeRoleSerializer(serializers.Serializer):
    """Serializer for role revocation requests."""

    role_key = serializers.CharField()
    metadata = serializers.JSONField(required=False)