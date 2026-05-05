from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from communications.models import CommunicationAuditAction
from communications.models import CommunicationEscalation
from communications.models import CommunicationEscalationStatus
from communications.services.audit_service import CommunicationAuditService


class CommunicationEscalationService:
    """
    Manage thread escalations.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        thread,
        reason: str,
        escalated_by=None,
        metadata: dict | None = None,
    ) -> CommunicationEscalation:
        """
        Create an open escalation for a thread.
        """
        escalation = CommunicationEscalation.objects.create(
            website=thread.website,
            thread=thread,
            reason=reason,
            escalated_by=escalated_by,
            metadata=metadata or {},
        )

        CommunicationAuditService.log(
            website=thread.website,
            thread=thread,
            actor=escalated_by,
            action=CommunicationAuditAction.ESCALATION_CREATED,
            details={
                "escalation_id": escalation.pk,
                "reason": reason,
            },
        )

        return escalation

    @staticmethod
    @transaction.atomic
    def resolve(
        *,
        escalation,
        resolved_by,
        resolution_note: str = "",
    ) -> CommunicationEscalation:
        """
        Resolve an escalation.
        """
        escalation.status = CommunicationEscalationStatus.RESOLVED
        escalation.resolved_by = resolved_by
        escalation.resolved_at = timezone.now()
        escalation.resolution_note = resolution_note
        escalation.save(
            update_fields=[
                "status",
                "resolved_by",
                "resolved_at",
                "resolution_note",
            ],
        )

        CommunicationAuditService.log(
            website=escalation.website,
            thread=escalation.thread,
            actor=resolved_by,
            action=CommunicationAuditAction.ESCALATION_RESOLVED,
            details={
                "escalation_id": escalation.id,
                "resolution_note": resolution_note,
            },
        )

        return escalation