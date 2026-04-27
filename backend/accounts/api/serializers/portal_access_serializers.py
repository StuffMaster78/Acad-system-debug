from __future__ import annotations

from rest_framework import serializers

from accounts.models import PortalAccess, PortalDefinition


class PortalDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortalDefinition
        fields = [
            "id",
            "code",
            "name",
            "domain",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PortalAccessSerializer(serializers.ModelSerializer):
    portal_code = serializers.CharField(
        source="portal.code",
        read_only=True,
    )
    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = PortalAccess
        fields = [
            "id",
            "user",
            "user_email",
            "portal",
            "portal_code",
            "is_active",
            "granted_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]