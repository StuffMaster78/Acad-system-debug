from datetime import timedelta

from django.utils import timezone

from audit_logging.models.audit_event import AuditEvent


class AuditCleanupService:

    @staticmethod
    def purge_old_events(days: int = 365):

        cutoff = timezone.now() - timedelta(days=days)

        return (
            AuditEvent.objects
            .filter(occurred_at__lt=cutoff)
            .delete()
        )