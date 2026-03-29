from rest_framework import serializers

from accounts.models import AccountRole
from accounts.api.serializers.role_definition_serializer import (
    RoleDefinitionSerializer,
)


class AccountRoleSerializer(serializers.ModelSerializer):
    """Serializer for account role reads."""

    role = RoleDefinitionSerializer(read_only=True)

    class Meta:
        model = AccountRole
        fields = [
            "id",
            "website",
            "account_profile",
            "role",
            "is_active",
            "assigned_by",
            "assigned_at",
            "expires_at",
            "metadata",
        ]
        read_only_fields = fields