from __future__ import annotations

from rest_framework import serializers

from accounts.models import TenantAccess


class TenantAccessSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )
    website_name = serializers.CharField(
        source="website.name",
        read_only=True,
    )

    class Meta:
        model = TenantAccess
        fields = [
            "id",
            "user",
            "user_email",
            "website",
            "website_name",
            "is_active",
            "granted_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]