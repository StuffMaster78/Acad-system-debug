import logging
from datetime import timedelta

from django.utils import timezone
from django.db import transaction

from audit_logging.models.audit_event import AuditEvent
from audit_logging.models.audit_dead_letter import AuditDeadLetter

logger = logging.getLogger("audit")


class AuditArchiveService:
    """
    Responsible for archiving audit data safely.

    RULES:
    - no business logic outside archival decisions
    - always batch-safe
    - always idempotent
    - never deletes without explicit constraint
    """

    # -------------------------
    # EVENT ARCHIVAL
    # -------------------------

    @staticmethod
    def archive_events_older_than(days: int, batch_size: int = 500) -> int:
        """
        Archives old audit events.

        Returns number of archived records.
        """

        cutoff = timezone.now() - timedelta(days=days)

        archived_count = 0

        while True:
            with transaction.atomic():
                qs = (
                    AuditEvent.objects
                    .select_for_update(skip_locked=True)
                    .filter(occurred_at__lt=cutoff)
                    .order_by("occurred_at")[:batch_size]
                )

                events = list(qs)

                if not events:
                    break

                for event in events:
                    AuditArchiveService._archive_event(event)

                archived_count += len(events)

        return archived_count

    # -------------------------
    # SINGLE EVENT ARCHIVE
    # -------------------------

    @staticmethod
    def _archive_event(event: AuditEvent) -> None:
        """
        Safe archival unit.

        Strategy:
        - move sensitive events to DLQ if needed
        - otherwise mark as archived (soft delete pattern)
        """

        try:
            if event.is_sensitive:
                AuditArchiveService._move_sensitive_to_dlq(event)
                return

            # soft archive pattern (safer than delete)
            event.status = "archived"
            event.save(update_fields=["status"])

        except Exception as exc:
            logger.exception(
                "ARCHIVE_EVENT_FAILED",
                extra={
                    "audit_event_id": str(event.id),
                    "error": str(exc),
                },
            )

    # -------------------------
    # SENSITIVE ARCHIVAL PATH
    # -------------------------

    @staticmethod
    def _move_sensitive_to_dlq(event: AuditEvent) -> None:
        """
        Sensitive events are never silently deleted.
        They are moved to DLQ for forensic retention.
        """

        AuditDeadLetter.objects.create(
            event_id=event.id,
            website=event.website,
            event_payload={
                "audit_event_id": str(event.id),
                "action": event.action,
                "object_type": event.object_type,
                "object_id": event.object_id,
                "metadata": event.metadata,
                "correlation_id": event.correlation_id,
                "span_id": event.span_id,
            },
            error_message="Archived from retention policy (sensitive event)",
            retry_count=0,
        )

        event.status = "discarded"
        event.save(update_fields=["status"])

    # -------------------------
    # DLQ CLEANUP
    # -------------------------

    @staticmethod
    def purge_resolved_dlq(older_than_days: int = 30) -> int:
        """
        Cleans resolved DLQ entries safely.
        """

        cutoff = timezone.now() - timedelta(days=older_than_days)

        qs = AuditDeadLetter.objects.filter(
            is_resolved=True,
            created_at__lt=cutoff,
        )

        count = qs.count()
        qs.delete()

        return count