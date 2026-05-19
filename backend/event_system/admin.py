from django.contrib import admin
from django.utils.html import format_html

from event_system.models.event_outbox import EventOutbox, EventStatus
from event_system.services.event_replay_service import EventReplayService

from event_system.models.event_audit_log import EventAuditLog
from event_system.services.event_timeline_service import EventTimelineService

@admin.register(EventOutbox)
class EventOutboxAdmin(admin.ModelAdmin):
    """
    Operational visibility for async events.
    """

    list_display = (
        "short_id",
        "event_type",
        "status_badge",
        "attempts",
        "created_at",
        "processed_at",
        "ignored_at",
    )

    list_filter = (
        "status",
        "event_type",
        "created_at",
        "processed_at",
    )

    search_fields = (
        "id",
        "event_type",
    )

    readonly_fields = (
        "id",
        "event_type",
        "payload",
        "status",
        "attempts",
        "max_attempts",
        "last_error",
        "created_at",
        "updated_at",
        "processed_at",
        "ignored_at",
    )

    ordering = ("-created_at",)
    list_per_page = 50
    date_hierarchy = "created_at"

    actions = (
        "retry_events",
        "mark_ignored",
    )

    fieldsets = (
        ("Event", {
            "fields": ("id", "event_type", "status"),
        }),
        ("Payload", {
            "fields": ("payload",),
        }),
        ("Execution", {
            "fields": ("attempts", "max_attempts", "last_error"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at", "processed_at", "ignored_at"),
        }),
    )

    @admin.display(description="Event ID")
    def short_id(self, obj: EventOutbox) -> str:
        return str(obj.id)[:8]

    @admin.display(description="Status")
    def status_badge(self, obj: EventOutbox) -> str:
        """
        Safe badge renderer (no enum casting issues).
        """

        status_colors = {
            EventStatus.PENDING.value: "gray",
            EventStatus.PROCESSED.value: "green",
            EventStatus.FAILED.value: "orange",
            EventStatus.DEAD_LETTER.value: "darkred",
            EventStatus.IGNORED.value: "lightgray",
        }

        color = status_colors.get(obj.status, "black")

        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color,
            obj.status.upper(),
        )

    @admin.action(description="Retry failed/dead-letter events")
    def retry_events(self, request, queryset):
        updated = queryset.filter(
            status__in=[
                EventStatus.FAILED.value,
                EventStatus.DEAD_LETTER.value,
            ]
        ).update(
            status=EventStatus.PENDING.value,
            attempts=0,
            last_error="",
        )

        self.message_user(request, f"{updated} event(s) reset to pending.")

    @admin.action(description="Mark events as ignored")
    def mark_ignored(self, request, queryset):
        updated = queryset.exclude(
            status=EventStatus.PROCESSED.value,
        ).update(
            status=EventStatus.IGNORED.value,
        )

        self.message_user(request, f"{updated} event(s) marked as ignored.")

    @admin.action(description="Replay selected events safely")
    def replay_events(self, request, queryset):
        count = 0

        for event in queryset:
            EventReplayService.replay(
                event_id=str(event.id),
                reason="admin_bulk_replay",
            )
            count += 1

        self.message_user(request, f"{count} event(s) replayed.")

    @admin.action(description="Move to dead letter")
    def mark_dead_letter(self, request, queryset):
        updated = queryset.update(status=EventStatus.DEAD_LETTER)
        self.message_user(request, f"{updated} moved to dead letter.")

    @admin.action(description="Retry failed events")
    def retry_failed(self, request, queryset):
        for event in queryset.filter(status=EventStatus.FAILED):
            EventReplayService.replay(
                event_id=str(event.id),
                reason="admin_retry_failed",
            )

@admin.register(EventAuditLog)
class EventAuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "event_id",
        "event_type",
        "stage",
        "event_status",
        "retry_count",
        "created_at",
    )

    list_filter = (
        "event_type",
        "stage",
        "event_status",
    )

    search_fields = (
        "event_id",
        "event_type",
    )

    readonly_fields = (
        "event_id",
        "event_type",
        "stage",
        "message",
        "worker_id",
        "duration_ms",
        "correlation_id",
        "retry_count",
        "event_status",
        "created_at",
    )

    ordering = ("-created_at",)
    
    @admin.display(description="Event Timeline")
    def timeline_view(self, obj):
        timeline = EventTimelineService.get_event_timeline(
            event_id=str(obj.event_id)
        )

        html = "<br>".join(
            [
                f"{t.stage} | {t.event_status} | {t.created_at}"
                for t in timeline
            ]
        )

        return format_html(html)

    timeline_view.short_description = "Event Timeline" # type: ignore[attr-defined]
