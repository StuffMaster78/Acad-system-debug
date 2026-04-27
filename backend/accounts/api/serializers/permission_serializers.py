from __future__ import annotations

from rest_framework import serializers

from accounts.models import PermissionDefinition, RolePermission


class PermissionDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionDefinition
        fields = [
            "id",
            "code",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RolePermissionSerializer(serializers.ModelSerializer):
    permission_code = serializers.CharField(
        source="permission.code",
        read_only=True,
    )
    role_name = serializers.CharField(
        source="role.label",
        read_only=True,
    )

    class Meta:
        model = RolePermission
        fields = [
            "id",
            "role",
            "role_name",
            "permission",
            "permission_code",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]