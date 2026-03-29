from rest_framework import serializers

from accounts.models import OnboardingSession


class OnboardingSessionSerializer(serializers.ModelSerializer):
    """Serializer for onboarding session reads."""

    class Meta:
        model = OnboardingSession
        fields = [
            "id",
            "website",
            "user",
            "account_profile",
            "onboarding_type",
            "target_role",
            "status",
            "started_at",
            "completed_at",
            "expires_at",
            "last_step",
            "metadata",
            "created_by",
            "updated_at",
        ]
        read_only_fields = fields