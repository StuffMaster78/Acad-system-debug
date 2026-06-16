from rest_framework import serializers

from audit_logging.models.audit_dead_letter import AuditDeadLetter


class AuditDeadLetterSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuditDeadLetter

        fields = (
            "id",
            "event_id",
            "event_payload",
            "error_message",
            "retry_count",
            "max_retries",
            "is_resolved",
            "failed_at",
        )

        read_only_fields = fields