# superadmin_management/services/audit_integrity_service.py

import logging

logger = logging.getLogger(__name__)


class AuditIntegrityService:
    """
    Ensures governance actions always have audit coverage.
    """

    @staticmethod
    def verify_audit_exists(action: str, obj_id: int):
        from audit_logging.models.audit_event import AuditEvent

        exists = AuditEvent.objects.filter(
            action=action,
            object_id=obj_id,
        ).exists()

        if not exists:
            logger.critical(
                "AUDIT MISSING action=%s object_id=%s",
                action,
                obj_id,
            )
            return False

        return True