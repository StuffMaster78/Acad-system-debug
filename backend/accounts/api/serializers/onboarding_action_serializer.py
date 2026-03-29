from rest_framework import serializers


class ClientOnboardingSerializer(serializers.Serializer):
    """Serializer for client onboarding actions."""

    metadata = serializers.JSONField(required=False)


class WriterOnboardingSerializer(serializers.Serializer):
    """Serializer for writer onboarding actions."""

    require_review = serializers.BooleanField(required=False, default=True)
    metadata = serializers.JSONField(required=False)


class StaffOnboardingSerializer(serializers.Serializer):
    """Serializer for staff onboarding actions."""

    role_keys = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )
    metadata = serializers.JSONField(required=False)