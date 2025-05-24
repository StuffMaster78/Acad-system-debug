from rest_framework import serializers
from audit_logging.models import AuditLogEntry


class AuditLogEntrySerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(
        source="actor.username", read_only=True
    )

    class Meta:
        model = AuditLogEntry
        fields = [
            "id", "action", "actor", "actor_username", "target",
            "target_id", "metadata", "ip_address", "user_agent", 
            "timestamp"
        ]
        read_only_fields = fields