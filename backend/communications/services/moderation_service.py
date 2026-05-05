from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from communications.models.audit import (
    CommunicationAuditAction,
)
from communications.models.moderation import (
    CommunicationModerationFlag,
    CommunicationModerationStatus,
)
from communications.services.audit_service import (
    CommunicationAuditService,
)
from communications.services.notification_service import (
    CommunicationNotificationService,
)

class CommunicationModerationService:
    """
    Manage moderation flags and message visibility.
    """

    @staticmethod
    @transaction.atomic
    def flag_message(
        *,
        message,
        reason: str,
        severity: str,
        created_by=None,
        details: str = "",
        metadata: dict | None = None,
    ) -> CommunicationModerationFlag:
        """
        Create a moderation flag for a message.
        """
        flag = CommunicationModerationFlag.objects.create(
            website=message.website,
            thread=message.thread,
            message=message,
            reason=reason,
            severity=severity,
            details=details,
            created_by=created_by,
            metadata=metadata or {},
        )
        
        transaction.on_commit(
            lambda: CommunicationNotificationService.notify_message_flagged(
                message=message,
                flag=flag,
            ),
        )

        CommunicationAuditService.log(
            website=message.website,
            thread=message.thread,
            message=message,
            actor=created_by,
            action=CommunicationAuditAction.MODERATION_FLAGGED,
            details={
                "flag_id": flag.pk,
                "reason": reason,
                "severity": severity,
            },
        )

        return flag

    @staticmethod
    @transaction.atomic
    def resolve_flag(
        *,
        flag,
        resolved_by,
        resolution_note: str = "",
    ) -> CommunicationModerationFlag:
        """
        Resolve a moderation flag.
        """
        flag.status = CommunicationModerationStatus.RESOLVED
        flag.resolved_by = resolved_by
        flag.resolved_at = timezone.now()
        flag.resolution_note = resolution_note
        flag.save(
            update_fields=[
                "status",
                "resolved_by",
                "resolved_at",
                "resolution_note",
                "updated_at",
            ],
        )

        CommunicationAuditService.log(
            website=flag.website,
            thread=flag.thread,
            message=flag.message,
            actor=resolved_by,
            action=CommunicationAuditAction.MODERATION_RESOLVED,
            details={
                "flag_id": flag.id,
                "resolution_note": resolution_note,
            },
        )

        return flag

    @staticmethod
    @transaction.atomic
    def hide_message(
        *,
        message,
        actor,
        reason: str = "",
    ):
        """
        Hide a message from normal users.
        """
        message.status = "hidden"
        message.hidden_at = timezone.now()
        message.save(update_fields=["status", "hidden_at", "updated_at"])

        CommunicationAuditService.log(
            website=message.website,
            thread=message.thread,
            message=message,
            actor=actor,
            action=CommunicationAuditAction.MESSAGE_HIDDEN,
            details={"reason": reason},
        )

        return message