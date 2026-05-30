from __future__ import annotations

import logging
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

log = logging.getLogger(__name__)

VALID_ACTION_TYPES = {
    "blacklist_client",
    "promote_writer",
    "demote_writer",
    "writer_probation",
    "suspend_writer",
    "suspend_client",
}


class EscalationService:
    """
    Service layer for the EscalationLog workflow.

    Support agents raise escalations for actions that require admin
    approval (blacklisting, writer promotion/probation, suspension).
    Admins review and approve or reject.

    Responsibilities:
        1. Create a new escalation log with validation.
        2. Approve a pending escalation and execute the downstream action.
        3. Reject a pending escalation with a reason.
        4. Notify relevant parties at each step.
        5. Record SupportActivityLog entries.
    """

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        escalated_by,
        action_type: str,
        target_user,
        reason: str,
        website,
    ):
        """
        Raise a new escalation for admin review.

        Args:
            escalated_by: Support agent raising the escalation.
            action_type:  One of VALID_ACTION_TYPES.
            target_user:  The user the action will be applied to.
            reason:       Required explanation.
            website:      Tenant website scope.

        Returns:
            EscalationLog instance with status=pending.

        Raises:
            ValidationError: If action_type or reason is invalid.
        """
        if action_type not in VALID_ACTION_TYPES:
            raise ValidationError(
                f"Invalid action type '{action_type}'. "
                f"Must be one of: {', '.join(sorted(VALID_ACTION_TYPES))}."
            )

        if not reason.strip():
            raise ValidationError("Escalation reason is required.")

        from support_management.models import EscalationLog

        escalation = EscalationLog.objects.create(
            escalated_by=escalated_by,
            action_type=action_type,
            target_user=target_user,
            reason=reason,
            status="pending",
        )

        cls._log_activity(
            user=escalated_by,
            description=(
                f"Raised escalation #{escalation.pk}: "
                f"{action_type} for user {getattr(target_user, 'email', target_user.pk)}"
            ),
        )
        cls._notify_admins(
            website=website,
            escalation=escalation,
            event_key="system.alert",
            context={
                "title": f"New escalation: {action_type}",
                "message": (
                    f"{getattr(escalated_by, 'email', 'Support')} raised an "
                    f"escalation requiring your review. "
                    f"Action: {action_type}. Reason: {reason[:200]}"
                ),
            },
        )

        return escalation

    # ------------------------------------------------------------------
    # Approve
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def approve(
        cls,
        *,
        escalation,
        approved_by,
        notes: str = "",
    ):
        """
        Approve a pending escalation and execute the downstream action.

        Args:
            escalation:  EscalationLog instance to approve.
            approved_by: Admin user approving.
            notes:       Optional approval notes.

        Returns:
            Updated EscalationLog with status=approved.

        Raises:
            ValidationError: If escalation is not in pending status.
        """
        cls._ensure_pending(escalation)

        escalation.approve(approved_by)
        if notes:
            escalation.reason = f"{escalation.reason}\n\nApproval notes: {notes}"
            escalation.save(update_fields=["reason"])

        cls._execute_action(escalation=escalation, executed_by=approved_by)

        cls._log_activity(
            user=approved_by,
            description=(
                f"Approved escalation #{escalation.pk}: "
                f"{escalation.action_type} for "
                f"{getattr(escalation.target_user, 'email', escalation.target_user_id)}"
            ),
        )
        cls._notify_requester(
            escalation=escalation,
            event_key="system.alert",
            context={
                "title": f"Escalation approved: {escalation.action_type}",
                "message": f"Your escalation #{escalation.pk} was approved.",
            },
        )

        return escalation

    # ------------------------------------------------------------------
    # Reject
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def reject(
        cls,
        *,
        escalation,
        rejected_by,
        reason: str,
    ):
        """
        Reject a pending escalation.

        Args:
            escalation:  EscalationLog instance to reject.
            rejected_by: Admin user rejecting.
            reason:      Required rejection reason.

        Returns:
            Updated EscalationLog with status=rejected.

        Raises:
            ValidationError: If escalation is not pending or reason is empty.
        """
        cls._ensure_pending(escalation)

        if not reason.strip():
            raise ValidationError("A reason is required when rejecting an escalation.")

        escalation.reject(rejected_by, reason)

        cls._log_activity(
            user=rejected_by,
            description=(
                f"Rejected escalation #{escalation.pk}: "
                f"{escalation.action_type}. Reason: {reason[:200]}"
            ),
        )
        cls._notify_requester(
            escalation=escalation,
            event_key="system.alert",
            context={
                "title": f"Escalation rejected: {escalation.action_type}",
                "message": (
                    f"Your escalation #{escalation.pk} was rejected. "
                    f"Reason: {reason}"
                ),
            },
        )

        return escalation

    # ------------------------------------------------------------------
    # Downstream action execution
    # ------------------------------------------------------------------

    @classmethod
    def _execute_action(cls, *, escalation, executed_by) -> None:
        """
        Execute the approved action against the target user.

        Each action type delegates to the appropriate service so this
        service stays thin and doesn't own cross-domain logic.
        """
        action = escalation.action_type
        target = escalation.target_user

        try:
            if action == "blacklist_client":
                cls._blacklist_client(target=target, executed_by=executed_by)
            elif action in {"suspend_client", "suspend_writer"}:
                cls._suspend_user(target=target, executed_by=executed_by)
            elif action == "writer_probation":
                cls._put_writer_on_probation(
                    target=target,
                    executed_by=executed_by,
                    reason=escalation.reason,
                )
            elif action == "promote_writer":
                cls._promote_writer(target=target, executed_by=executed_by)
            elif action == "demote_writer":
                cls._demote_writer(target=target, executed_by=executed_by)
        except Exception as exc:
            log.exception(
                "EscalationService._execute_action failed: action=%s target=%s: %s",
                action,
                getattr(target, "pk", None),
                exc,
            )

    @staticmethod
    def _blacklist_client(*, target, executed_by) -> None:
        from client_management.models import BlacklistedEmail
        BlacklistedEmail.add_to_blacklist(
            email=target.email,
            reason=f"Escalation approved by {getattr(executed_by, 'email', executed_by.pk)}",
        )

    @staticmethod
    def _suspend_user(*, target, executed_by) -> None:
        try:
            profile = target.clientprofile
            from client_management.services.client_profile_service import (
                ClientProfileService,
            )
            ClientProfileService.suspend(
                client=profile,
                performed_by=executed_by,
                reason="Approved escalation",
            )
        except Exception:
            pass

    @staticmethod
    def _put_writer_on_probation(*, target, executed_by, reason: str) -> None:
        try:
            from writer_management.services.discipline_service import (
                DisciplineService,
            )
            DisciplineService.place_on_probation(
                writer=target,
                placed_by=executed_by,
                reason=reason,
            )
        except Exception:
            pass

    @staticmethod
    def _promote_writer(*, target, executed_by) -> None:
        try:
            from writer_management.services.level_progression_service import (
                LevelProgressionService,
            )
            LevelProgressionService.promote(
                writer=target,
                promoted_by=executed_by,
            )
        except Exception:
            pass

    @staticmethod
    def _demote_writer(*, target, executed_by) -> None:
        try:
            from writer_management.services.level_progression_service import (
                LevelProgressionService,
            )
            LevelProgressionService.demote(
                writer=target,
                demoted_by=executed_by,
            )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_pending(escalation) -> None:
        if escalation.status != "pending":
            raise ValidationError(
                f"Escalation #{escalation.pk} is already {escalation.status}. "
                "Only pending escalations can be reviewed."
            )

    @staticmethod
    def _log_activity(*, user, description: str) -> None:
        try:
            from support_management.models import SupportActivityLog
            SupportActivityLog.objects.create(
                user=user,
                action_type="escalated_case",
                description=description,
            )
        except Exception as exc:
            log.warning("EscalationService._log_activity failed: %s", exc)

    @staticmethod
    def _notify_admins(*, website, escalation, event_key: str, context: dict) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify_staff(
                event_key=event_key,
                website=website,
                context=context,
                priority="high",
            )
        except Exception as exc:
            log.warning("EscalationService._notify_admins failed: %s", exc)

    @staticmethod
    def _notify_requester(*, escalation, event_key: str, context: dict) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            website = getattr(
                getattr(escalation.escalated_by, "supportprofile", None),
                "website",
                None,
            )
            if website is None:
                return
            NotificationService.notify(
                event_key=event_key,
                recipient=escalation.escalated_by,
                website=website,
                context=context,
            )
        except Exception as exc:
            log.warning("EscalationService._notify_requester failed: %s", exc)
