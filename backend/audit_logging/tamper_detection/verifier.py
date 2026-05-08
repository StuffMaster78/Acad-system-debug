from audit_logging.tamper_detection.hashing import (
    AuditHashingService,
)

class AuditIntegrityVerifier:

    @staticmethod
    def verify(event):

        payload = {
            "id": str(event.id),
            "action": event.action,
            "occurred_at": str(event.occurred_at),
            "previous_hash": event.previous_hash,
        }

        expected = AuditHashingService.compute_hash(payload)

        return expected == event.integrity_hash