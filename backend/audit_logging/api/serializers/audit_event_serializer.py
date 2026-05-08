from rest_framework import serializers

from audit_logging.models.audit_event import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuditEvent

        fields = (
            "id",
            "website",
            "occurred_at",
            "actor_id",
            "action",
            "object_type",
            "object_id",
            "status",
            "processed_at",
            "processing_attempts",
            "correlation_id",
            "span_id",
            "severity",
            "is_sensitive",
            "sensitivity_level",
            "service_name",
            "metadata",
        )

        read_only_fields = fields


class SensitiveAuditEventSerializer(AuditEventSerializer):
    """
    Elevated serializer for privileged audit viewers.
    """

    class Meta(AuditEventSerializer.Meta):

        fields = (
            *AuditEventSerializer.Meta.fields,
            "ip_address",
            "user_agent",
            "last_error",
            "idempotency_key",
            "event_version",
        )

        read_only_fields = fields