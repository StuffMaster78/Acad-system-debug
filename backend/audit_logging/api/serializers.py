from rest_framework import serializers
from audit_logging.storage.models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = [
            "event_id",
            "action",
            "actor_id",
            "actor_type",
            "object_type",
            "object_id",
            "request_id",
            "correlation_id",
            "ip_address",
            "user_agent",
            "span_id",
            "span_name",
            "span_start_ms",
            "span_duration_ms",
            "metadata",
            "is_sensitive",
            "sensitivity_level",
            "source",
            "created_at",
        ]
        read_only_fields = fields

class AuditEventFilterSerializer(serializers.Serializer):
    action = serializers.CharField(required=False)
    actor_id = serializers.CharField(required=False)
    object_id = serializers.CharField(required=False)
    correlation_id = serializers.CharField(required=False)

    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)

    is_sensitive = serializers.BooleanField(required=False)


class AuditTraceSerializer(serializers.Serializer):
    correlation_id = serializers.CharField()
    span_id = serializers.CharField()
    span_name = serializers.CharField()
    duration_ms = serializers.FloatField(allow_null=True)