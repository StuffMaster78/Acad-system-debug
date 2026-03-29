from rest_framework import serializers

from accounts.models import AccountProfile


class AccountProfileSerializer(serializers.ModelSerializer):
    """Serializer for account profile reads."""

    class Meta:
        model = AccountProfile
        fields = [
            "id",
            "website",
            "user",
            "status",
            "onboarding_status",
            "is_primary",
            "activated_at",
            "suspended_at",
            "suspension_reason",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields