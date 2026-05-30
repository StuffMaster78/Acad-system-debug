from __future__ import annotations

import logging
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

log = logging.getLogger(__name__)


class DisputeResolutionService:
    """
    Support-side dispute resolution workflow.

    The orders app owns the dispute model and the forensic audit trail.
    This service provides the support layer: assigning disputes to agents,
    recording resolution decisions, creating DisputeResolutionLog entries,
    and notifying parties.

    Responsibilities:
        1. Assign an open dispute to a support agent.
        2. Record a resolution decision with notes.
        3. Escalate a dispute to admin if the agent cannot resolve.
        4. Log all actions to SupportActivityLog.
        5. Notify client and writer of the outcome.
    """

    # ------------------------------------------------------------------
    # Assign
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def assign(
        cls,
        *,
        dispute,
        agent,
        assigned_by,
        reason: str = "",
    ):
        """
        Assign an open dispute to a support agent.

        Args:
            dispute:     OrderDispute instance.
            agent:       Support agent user to assign.
            assigned_by: Staff member making the assignment.
            reason:      Optional assignment reason.

        Returns:
            Updated dispute instance.
        """
        dispute.assigned_to = agent
        dispute.save(update_fields=["assigned_to", "updated_at"])

        cls._log_activity(
            user=assigned_by,
            dispute=dispute,
            action_type="resolved_dispute",
            description=(
                f"Dispute #{dispute.pk} assigned to "
                f"{getattr(agent, 'email', agent.pk)}"
                + (f". Reason: {reason}" if reason else "")
            ),
        )
        cls._notify_agent(dispute=dispute, agent=agent)

        return dispute

    # ------------------------------------------------------------------
    # Resolve
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def resolve(
        cls,
        *,
        dispute,
        resolved_by,
        resolution: str,
        notes: str,
        outcome: str = "resolved",
    ):
        """
        Record a resolution decision and close the dispute.

        Args:
            dispute:     OrderDispute instance.
            resolved_by: Support agent resolving the dispute.
            resolution:  Human-readable resolution summary.
            notes:       Internal resolution notes.
            outcome:     Outcome label (resolved, resolved_for_client,
                         resolved_for_writer). Default: resolved.

        Returns:
            Updated dispute instance.

        Raises:
            ValidationError: If the dispute is already resolved or notes missing.
        """
        cls._ensure_open(dispute)

        if not notes.strip():
            raise ValidationError(
                "Resolution notes are required when resolving a dispute."
            )

        now = timezone.now()

        # Mark the dispute resolved via the orders domain service.
        cls._mark_dispute_resolved(
            dispute=dispute,
            resolved_by=resolved_by,
            resolution=resolution,
            outcome=outcome,
        )

        # Create the support-side resolution log entry.
        cls._create_resolution_log(
            dispute=dispute,
            resolved_by=resolved_by,
            notes=notes,
            resolved_at=now,
        )

        cls._log_activity(
            user=resolved_by,
            dispute=dispute,
            action_type="resolved_dispute",
            description=(
                f"Dispute #{dispute.pk} resolved. "
                f"Outcome: {outcome}. Notes: {notes[:200]}"
            ),
        )
        cls._notify_parties(dispute=dispute, outcome=outcome, resolution=resolution)

        return dispute

    # ------------------------------------------------------------------
    # Escalate
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def escalate(
        cls,
        *,
        dispute,
        escalated_by,
        reason: str,
        website,
    ):
        """
        Escalate a dispute to admin when support cannot resolve it.

        Creates an EscalationLog and notifies admin staff.

        Args:
            dispute:      OrderDispute to escalate.
            escalated_by: Support agent escalating.
            reason:       Required escalation reason.
            website:      Tenant website.

        Returns:
            EscalationLog instance.
        """
        if not reason.strip():
            raise ValidationError("Escalation reason is required.")

        from support_management.models import EscalationLog

        escalation = EscalationLog.objects.create(
            escalated_by=escalated_by,
            action_type="blacklist_client",  # Closest available type — ops reviews
            target_user=getattr(dispute, "client", escalated_by),
            reason=f"Dispute #{dispute.pk} escalation: {reason}",
            status="pending",
        )

        dispute.status = "escalated"
        dispute.save(update_fields=["status", "updated_at"])

        cls._log_activity(
            user=escalated_by,
            dispute=dispute,
            action_type="escalated_case",
            description=(
                f"Dispute #{dispute.pk} escalated to admin. Reason: {reason[:200]}"
            ),
        )

        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify_staff(
                event_key="system.alert",
                website=website,
                context={
                    "title": f"Dispute #{dispute.pk} escalated",
                    "message": (
                        f"Dispute #{dispute.pk} was escalated by "
                        f"{getattr(escalated_by, 'email', 'support')}. "
                        f"Reason: {reason[:200]}"
                    ),
                },
                priority="high",
            )
        except Exception as exc:
            log.warning("DisputeResolutionService._escalate notify failed: %s", exc)

        return escalation

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_open(dispute) -> None:
        closed_statuses = {"resolved", "closed", "escalated"}
        if getattr(dispute, "status", "") in closed_statuses:
            raise ValidationError(
                f"Dispute #{dispute.pk} is already {dispute.status} "
                "and cannot be resolved again."
            )

    @staticmethod
    def _mark_dispute_resolved(
        *,
        dispute,
        resolved_by,
        resolution: str,
        outcome: str,
    ) -> None:
        """Delegate to the orders domain dispute service."""
        try:
            from orders.services.dispute_orchestration_service import (
                DisputeOrchestrationService,
            )
            DisputeOrchestrationService.resolve_dispute(
                dispute=dispute,
                resolved_by=resolved_by,
                resolution=resolution,
                outcome=outcome,
            )
        except Exception as exc:
            log.warning(
                "_mark_dispute_resolved: orders service failed for "
                "dispute=%s: %s. Falling back to direct save.",
                dispute.pk,
                exc,
            )
            dispute.status = "resolved"
            dispute.resolved_at = timezone.now()
            dispute.save(update_fields=["status", "resolved_at", "updated_at"])

    @staticmethod
    def _create_resolution_log(
        *,
        dispute,
        resolved_by,
        notes: str,
        resolved_at,
    ) -> None:
        try:
            from support_management.models import (
                DisputeResolutionLog,
                SupportProfile,
            )
            support_profile = SupportProfile.objects.filter(
                user=resolved_by
            ).first()

            DisputeResolutionLog.objects.update_or_create(
                dispute=dispute,
                defaults={
                    "resolved_by": support_profile,
                    "resolution_notes": notes,
                    "resolved_at": resolved_at,
                },
            )
        except Exception as exc:
            log.warning(
                "_create_resolution_log failed for dispute=%s: %s", dispute.pk, exc
            )

    @staticmethod
    def _log_activity(*, user, dispute, action_type: str, description: str) -> None:
        try:
            from support_management.models import SupportActivityLog
            SupportActivityLog.objects.create(
                user=user,
                action_type=action_type,
                related_dispute=dispute,
                description=description,
            )
        except Exception as exc:
            log.warning("DisputeResolutionService._log_activity failed: %s", exc)

    @staticmethod
    def _notify_agent(*, dispute, agent) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            website = getattr(dispute, "website", None) or getattr(
                getattr(dispute, "order", None), "website", None
            )
            if website is None:
                return
            NotificationService.notify(
                event_key="ticket.assigned",
                recipient=agent,
                website=website,
                context={
                    "ticket_id": dispute.pk,
                    "ticket_title": f"Dispute #{dispute.pk}",
                    "ticket_status": getattr(dispute, "status", ""),
                },
            )
        except Exception as exc:
            log.warning("DisputeResolutionService._notify_agent failed: %s", exc)

    @staticmethod
    def _notify_parties(*, dispute, outcome: str, resolution: str) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            order = getattr(dispute, "order", None)
            website = getattr(dispute, "website", None) or getattr(
                order, "website", None
            )
            if website is None:
                return

            context = {
                "order_id": getattr(order, "pk", None),
                "dispute_id": dispute.pk,
                "outcome": outcome,
                "resolution": resolution[:300],
            }

            client = getattr(order, "client", None)
            if client:
                NotificationService.notify(
                    event_key="order.dispute_resolved",
                    recipient=client,
                    website=website,
                    context=context,
                )

            writer_user = getattr(order, "assigned_writer", None)
            if writer_user:
                NotificationService.notify(
                    event_key="order.dispute_resolved",
                    recipient=writer_user,
                    website=website,
                    context=context,
                )
        except Exception as exc:
            log.warning("DisputeResolutionService._notify_parties failed: %s", exc)
