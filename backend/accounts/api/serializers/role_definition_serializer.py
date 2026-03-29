from rest_framework import serializers

from accounts.models import RoleDefinition


class RoleDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for role definition reads."""

    class Meta:
        model = RoleDefinition
        fields = [
            "id",
            "website",
            "key",
            "name",
            "description",
            "is_system_role",
            "is_active",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields