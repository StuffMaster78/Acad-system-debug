from rest_framework import serializers

from accounts.models import AccountAuditLog


class AccountAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for account audit log reads."""

    class Meta:
        model = AccountAuditLog
        fields = [
            "id",
            "website",
            "user",
            "account_profile",
            "event_type",
            "description",
            "actor",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields