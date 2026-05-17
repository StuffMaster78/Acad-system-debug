from __future__ import annotations

from rest_framework import serializers

from superadmin_management.commands.models import Command


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = [
            "id",
            "tenant_id",
            "actor_id",
            "command_type",
            "payload",
            "status",
            "requires_approval",
            "correlation_id",
            "created_at",
            "updated_at",
        ]