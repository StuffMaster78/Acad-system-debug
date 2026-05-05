from __future__ import annotations

from rest_framework import serializers

from communications.models.audit import CommunicationAuditLog


class CommunicationAuditLogSerializer(serializers.ModelSerializer):
    """
    Read serializer for communication audit logs.
    """

    actor_display = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationAuditLog
        fields = [
            "id",
            "website",
            "thread",
            "message",
            "actor",
            "actor_display",
            "action",
            "details",
            "ip_address",
            "user_agent",
            "created_at",
        ]
        read_only_fields = fields

    def get_actor_display(self, obj: CommunicationAuditLog) -> str:
        """
        Return actor display label.
        """
        if obj.actor is None:
            return "System"

        if hasattr(obj.actor, "get_full_name"):
            full_name = obj.actor.get_full_name()
            if full_name:
                return full_name

        return getattr(obj.actor, "email", str(obj.actor))