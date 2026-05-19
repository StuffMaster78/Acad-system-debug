import json

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from audit_logging.models.audit_dead_letter import AuditDeadLetter
from audit_logging.models.audit_event import AuditEvent


# --------------------------------------------------
# Audit Event Admin
# --------------------------------------------------


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "website",
        "action",
        "actor_id",
        "status",
        "severity",
        "is_sensitive",
        "processing_attempts",
        "occurred_at",
        "trace_links",
    )

    list_filter = (
        "status",
        "severity",
        "is_sensitive",
        "website",
        "occurred_at",
    )

    search_fields = (
        "id",
        "action",
        "actor_id",
        "object_type",
        "object_id",
        "correlation_id",
        "span_id",
        "idempotency_key",
    )

    readonly_fields = (
        "id",
        "trace_links",
        "pretty_metadata",
        "website",
        "action",
        "actor_id",
        "object_type",
        "object_id",
        "metadata",
        "correlation_id",
        "span_id",
        "ip_address",
        "user_agent",
        "severity",
        "is_sensitive",
        "sensitivity_level",
        "service_name",
        "idempotency_key",
        "event_version",
        "occurred_at",
        "processed_at",
        "processing_attempts",
        "last_error",
        "status",
    )

    ordering = ("-occurred_at",)

    # --------------------------------------------------
    # Permissions
    # --------------------------------------------------

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _changelist_url(self) -> str:
        return reverse("admin:audit_logging_auditevent_changelist")

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    @admin.display(description="Navigation")
    def trace_links(self, obj: AuditEvent):

        url = self._changelist_url()

        return format_html(
            """
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <a href="{}?correlation_id__exact={}">Trace</a>
                <a href="{}?actor_id__exact={}">Actor</a>
                <a href="{}?object_type__exact={}&object_id__exact={}">Object</a>
            </div>
            """,
            url,
            obj.correlation_id or "",
            url,
            obj.actor_id or "",
            url,
            obj.object_type or "",
            obj.object_id or "",
        )

    # --------------------------------------------------
    # Metadata rendering
    # --------------------------------------------------

    @admin.display(description="Metadata")
    def pretty_metadata(self, obj: AuditEvent):

        try:
            formatted = json.dumps(
                obj.metadata or {},
                indent=2,
                sort_keys=True,
            )

            return format_html(
                "<pre style='white-space: pre-wrap; margin:0;'>{}</pre>",
                formatted,
            )

        except Exception:
            return "Invalid JSON"


# --------------------------------------------------
# Dead Letter Queue Admin
# --------------------------------------------------


@admin.register(AuditDeadLetter)
class AuditDeadLetterAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "event_id",
        "retry_count",
        "is_resolved",
        "failed_at",
        "resolution_status",
    )

    list_filter = (
        "is_resolved",
        "retry_count",
        "failed_at",
    )

    search_fields = (
        "event_id",
        "error_message",
    )

    readonly_fields = (
        "id",
        "event_id",
        "event_payload",
        "pretty_payload",
        "error_message",
        "retry_count",
        "is_resolved",
        "failed_at",
    )

    ordering = ("-failed_at",)

    # --------------------------------------------------
    # Permissions
    # --------------------------------------------------

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # --------------------------------------------------
    # Resolution display
    # --------------------------------------------------

    @admin.display(description="Resolution")
    def resolution_status(self, obj: AuditDeadLetter):

        if obj.is_resolved:
            return format_html(
                "<span style='color:green; font-weight:bold;'>✓ Resolved</span>"
            )

        return format_html(
            "<span style='color:#b58900; font-weight:bold;'>Pending</span>"
        )

    # --------------------------------------------------
    # Payload rendering
    # --------------------------------------------------

    @admin.display(description="Payload")
    def pretty_payload(self, obj: AuditDeadLetter):

        try:
            formatted = json.dumps(
                obj.event_payload or {},
                indent=2,
                sort_keys=True,
            )

            return format_html(
                "<pre style='white-space: pre-wrap; margin:0;'>{}</pre>",
                formatted,
            )

        except Exception:
            return "Invalid JSON"
