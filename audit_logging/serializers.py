from rest_framework import serializers
from audit_logging.models import AuditLogEntry


class AuditLogEntrySerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(
        source="actor.username", read_only=True
    )
    target_object_repr = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    changes = serializers.JSONField(
        help_text="Changes made during the action, formatted as {field: {'from': old_value, 'to': new_value}}.",
        required=False
    )

    notes = serializers.CharField(
        allow_blank=True,
        help_text="Optional notes or comments about the action.",
        required=False
    )

    request_id = serializers.CharField(
        max_length=64,
        allow_blank=True,
        help_text="Unique identifier for the request, useful for tracing actions."
    )
    metadata_note = serializers.SerializerMethodField()
    request_method = serializers.SerializerMethodField()
    status_code = serializers.SerializerMethodField()
    readable_changes = serializers.SerializerMethodField()
    class Meta:
        model = AuditLogEntry
        fields = [
            "id", "action", "actor", "actor_username", "target",
            "target_id", "metadata", "ip_address", "user_agent", 
            "timestamp", "target_object_repr", "metadata_note",
            "changes", "notes", "request_id", "readable_changes"
            "request_method", "status_code"
        ]
        read_only_fields = fields
        search_fields = [
            'action', 'target', 'actor__username',
            'metadata__note', 'metadata__status',
            'changes__status__from', 'changes__status__to',
            'changes__price__from', 'changes__price__to'
        ]


    def get_target_object_repr(self, obj):
        """
        Returns a string representation of the target object.
        If the target is a model instance, it returns its string representation.
        Otherwise, it returns the target as is.
        """
        if obj.target_object:
            return str(obj.target_object)
        return obj.target
    

    def get_metadata_note(self, obj):
        return obj.metadata.get("note") if obj.metadata else None
    
    def get_request_method(self, obj):
        """
        Returns the HTTP method used in the request, if available.
        """
        return obj.metadata.get("method", "N/A") if obj.metadata else "N/A"
    
    def get_status_code(self, obj):
        """
        Returns the HTTP status code from the metadata, if available.
        """
        return obj.metadata.get("status") if obj.metadata else None
    
    def get_readable_changes(self, obj):
        if not obj.changes:
            return None
        return [
            {
                "field": field,
                "from": change.get("from"),
                "to": change.get("to"),
                "delta": f"{change.get('from')} → {change.get('to')}"
            }
            for field, change in obj.changes.items()
        ]