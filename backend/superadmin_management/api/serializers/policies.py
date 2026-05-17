from __future__ import annotations

from rest_framework import serializers

from governance.policies.models import Policy


class PolicySerializer(serializers.ModelSerializer):
    """
    Policy graph is stored as JSON (nodes + edges).
    Frontend renders this as a visual editor.
    """

    class Meta:
        model = Policy
        fields = [
            "id",
            "name",
            "description",
            "tenant_id",
            "version",
            "is_active",
            "effect",
            "rule",
            "priority",
            "created_at",
        ]


class PolicyGraphPreviewSerializer(serializers.Serializer):
    """
    Optional helper serializer for UI simulation mode.
    Used when frontend runs 'simulate command against policy graph'.
    """

    command_type = serializers.CharField()
    actor_id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    payload = serializers.JSONField()