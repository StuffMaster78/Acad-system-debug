from audit_logging.models.audit_event import AuditEvent
from audit_logging.tamper_detection.hashing import (
    AuditHashingService,
)


class AuditChainService:

    @staticmethod
    def attach_integrity(event: AuditEvent):

        previous = (
            AuditEvent.objects
            .order_by("-occurred_at")
            .first()
        )

        previous_hash = (
            previous.integrity_hash
            if previous
            else None
        )

        payload = {
            "id": str(event.id),
            "action": event.action,
            "occurred_at": str(event.occurred_at),
            "previous_hash": previous_hash,
        }

        event.previous_hash = previous_hash

        event.integrity_hash = (
            AuditHashingService.compute_hash(payload)
        )