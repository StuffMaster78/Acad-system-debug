"""
CHANGES FROM PREVIOUS VERSION
------------------------------
1. Removed phantom import: OrderTransitionHelper does not exist.
   Replaced with OrderTransitionService throughout.

2. submit_review() approval branch:
   UNDER_EDITING → REVIEWED  (WRONG — REVIEWED is post-client-rating)
   UNDER_EDITING → SUBMITTED (CORRECT — delivered to client)

3. submit_review() revision branch:
   order.status = ... ; order.save()  (WRONG — no timeline event)
   OrderTransitionService.transition(...)  (CORRECT — creates timeline event)

4. submit_review() audit call:
   Syntax error fixed — service_name was inside metadata dict closing brace.

5. reject_task() notification:
   Dead loop (User.objects.filter → for admin in admins → notify_role)
   Replaced with single notify_role() call. User import removed.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.timezone import now

from audit_logging.services.audit_service import AuditService
from editor_management.models import (
    EditorActionLog,
    EditorProfile,
    EditorReviewSubmission,
    EditorTaskAssignment,
)
from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.models.orders.enums import OrderStatus

# FIX 1: was OrderTransitionHelper — module does not exist
from orders.services.order_transition_service import OrderTransitionService

logger = logging.getLogger(__name__)


class EditorReviewService:
    """
    Handles editor review submission and task completion.
    """

    @staticmethod
    @transaction.atomic
    def start_review(
        task_assignment: EditorTaskAssignment,
        editor: EditorProfile,
    ) -> EditorTaskAssignment:
        """Start reviewing an assigned task."""
        if task_assignment.assigned_editor != editor:
            raise ValidationError(
                "Only the assigned editor can start reviewing this task."
            )

        task_assignment.start_review()

        EditorActionLog.objects.create(
            editor=editor,
            action_type="started_review",
            action=f"Started reviewing order {task_assignment.order.pk}",
            related_order=task_assignment.order,
            related_task=task_assignment,
        )

        AuditService.record(
            action="editor.review.started",
            actor=editor.user,
            obj=task_assignment.order,
            website=task_assignment.order.website,
            metadata={"review_status": "in_review"},
            service_name="editor_management",
        )

        return task_assignment

    @staticmethod
    @transaction.atomic
    def submit_review(
        task_assignment: EditorTaskAssignment,
        editor: EditorProfile,
        quality_score: Optional[Decimal] = None,
        issues_found: str = "",
        corrections_made: str = "",
        recommendations: str = "",
        is_approved: bool = True,
        requires_revision: bool = False,
        revision_notes: str = "",
        edited_files: Optional[list] = None,
    ) -> EditorReviewSubmission:
        """Submit a review for an order."""
        if task_assignment.assigned_editor != editor:
            raise ValidationError(
                "Only the assigned editor can submit a review for this task."
            )

        if task_assignment.review_status != "in_review":
            raise ValidationError(
                f"Cannot submit review from status: "
                f"{task_assignment.review_status}"
            )

        order = task_assignment.order

        if quality_score is not None:
            if not (Decimal("0.00") <= quality_score <= Decimal("10.00")):
                raise ValidationError(
                    "Quality score must be between 0.00 and 10.00."
                )

        review_submission, created = EditorReviewSubmission.objects.get_or_create(
            task_assignment=task_assignment,
            defaults={
                "editor":            editor,
                "order":             order,
                "quality_score":     quality_score,
                "issues_found":      issues_found,
                "corrections_made":  corrections_made,
                "recommendations":   recommendations,
                "is_approved":       is_approved,
                "requires_revision": requires_revision,
                "revision_notes":    revision_notes,
                "edited_files":      edited_files or [],
            },
        )

        if not created:
            review_submission.quality_score    = quality_score
            review_submission.issues_found     = issues_found
            review_submission.corrections_made = corrections_made
            review_submission.recommendations  = recommendations
            review_submission.is_approved      = is_approved
            review_submission.requires_revision = requires_revision
            review_submission.revision_notes   = revision_notes
            review_submission.edited_files     = edited_files or []
            review_submission.save()

        if is_approved and not requires_revision:
            # Editor approved — complete task, deliver to client

            task_assignment.complete_review()

            # FIX 2: was REVIEWED (post-client-rating — wrong)
            #        was OrderTransitionHelper (doesn't exist — ImportError)
            # CORRECT: SUBMITTED = delivered to client
            if order.status == OrderStatus.UNDER_EDITING.value:
                OrderTransitionService.transition(
                    order=order,
                    next_status=OrderStatus.SUBMITTED.value,
                    actor=editor.user,
                    event_type="editor_approved_submitted_to_client",
                    metadata={
                        "editor_profile_id": getattr(editor, "id", None),
                        "editor_task_id": getattr(task_assignment, "id", None),
                    },
                )

            EditorActionLog.objects.create(
                editor=editor,
                action_type="submitted_review",
                action=f"Submitted review for order {order.pk} — Approved",
                related_order=order,
                related_task=task_assignment,
                metadata={
                    "quality_score": float(quality_score) if quality_score else None,
                    "is_approved":   True,
                },
            )

            if order.client:
                _notify(
                    event_key="order.reviewed",
                    recipient=order.client,
                    website=order.website,
                    context={
                        "order_id": order.pk,
                        "order_topic": order.topic,
                        "reviewed_by": editor.name,
                        "approved":    True,
                    },
                    is_critical=True,
                )

        else:
            # Requires revision from writer
            task_assignment.notes = (
                (task_assignment.notes or "") +
                f"\n[Revision Required: {revision_notes}]"
            )
            task_assignment.save(update_fields=["notes", "updated_at"])

            # FIX 3: was direct order.status = ...; order.save()
            # No timeline event was created. Service handles that.
            if order.status == OrderStatus.UNDER_EDITING.value:
                OrderTransitionService.transition(
                    order=order,
                    next_status=OrderStatus.REVISION_REQUESTED.value,
                    actor=editor.user,
                    event_type="editor_revision_requested",
                    metadata={
                        "revision_notes": revision_notes,
                        "editor_task_id": getattr(task_assignment, "id", None),
                    },
                )

            EditorActionLog.objects.create(
                editor=editor,
                action_type="submitted_review",
                action=(
                    f"Submitted review for order {order.pk}"
                    f" — Revision Required"
                ),
                related_order=order,
                related_task=task_assignment,
                metadata={
                    "quality_score":     float(quality_score) if quality_score else None,
                    "requires_revision": True,
                },
            )

            if order.assigned_writer:
                _notify(
                    event_key="order.revision_requested",
                    recipient=order.assigned_writer,
                    website=order.website,
                    context={
                        "order_id": order.pk,
                        "order_topic": order.topic,
                        "revision_notes": revision_notes,
                        "requested_by":   editor.name,
                    },
                    is_critical=True,
                )

        # FIX 4: syntax error — service_name was inside metadata dict
        AuditService.record(
            action="editor.review.submitted",
            actor=editor.user,
            obj=order,
            website=order.website,
            metadata={
                "review_submission_id": review_submission.pk,
                "is_approved": is_approved,
                "requires_revision": requires_revision,
            },
            service_name="editor_management",
        )

        return review_submission

    @staticmethod
    @transaction.atomic
    def complete_task(
        task_assignment: EditorTaskAssignment,
        editor: EditorProfile,
        final_notes: str = "",
    ) -> EditorTaskAssignment:
        """Mark a task as completed after review submitted and approved."""
        if task_assignment.assigned_editor != editor:
            raise ValidationError(
                "Only the assigned editor can complete this task."
            )

        if task_assignment.review_status not in ["in_review", "completed"]:
            raise ValidationError(
                f"Cannot complete task from status: "
                f"{task_assignment.review_status}"
            )

        if not hasattr(task_assignment, "review_submission"):
            raise ValidationError(
                "Cannot complete task without submitting a review first."
            )

        task_assignment.complete_review()

        if final_notes:
            task_assignment.notes = (
                (task_assignment.notes or "") +
                f"\n[Final Notes: {final_notes}]"
            )
            task_assignment.save(update_fields=["notes", "updated_at"])

        EditorActionLog.objects.create(
            editor=editor,
            action_type="completed_task",
            action=f"Completed task for order {task_assignment.order.pk}",
            related_order=task_assignment.order,
            related_task=task_assignment,
        )

        AuditService.record(
            action="editor.task.completed",
            actor=editor.user,
            obj=task_assignment.order,
            website=task_assignment.order.website,
            metadata={"review_status": "completed"},
            service_name="editor_management",
        )

        return task_assignment

    @staticmethod
    @transaction.atomic
    def reject_task(
        task_assignment: EditorTaskAssignment,
        editor: EditorProfile,
        reason: str,
    ) -> EditorTaskAssignment:
        """Reject a task — order needs admin review."""
        if task_assignment.assigned_editor != editor:
            raise ValidationError(
                "Only the assigned editor can reject this task."
            )

        task_assignment.review_status = "rejected"
        task_assignment.notes = (
            (task_assignment.notes or "") +
            f"\n[Rejected: {reason}]"
        )
        task_assignment.reviewed_at = now()
        task_assignment.save(update_fields=[
            "review_status", "notes", "reviewed_at", "updated_at"
        ])

        EditorActionLog.objects.create(
            editor=editor,
            action_type="rejected_task",
            action=f"Rejected task for order {task_assignment.order.pk}",
            related_order=task_assignment.order,
            related_task=task_assignment,
            metadata={"reason": reason},
        )

        AuditService.record(
            action="editor.task.rejected",
            actor=editor.user,
            obj=task_assignment.order,
            website=task_assignment.order.website,
            metadata={"review_status": "rejected", "reason": reason},
            service_name="editor_management",
        )

        # FIX 5: was dead loop — User.objects.filter → for admin → notify_role
        # notify_role handles all admin recipients internally
        _notify_role(
            event_key="editor.task_rejected",
            role="admin",
            website=task_assignment.order.website,
            context={
                "order_id": task_assignment.order.pk,
                "editor":   editor.name,
                "reason":   reason,
            },
            is_critical=True,
        )

        return task_assignment


# ----------------------------------------------------------------
# PRIVATE NOTIFICATION HELPERS
# ----------------------------------------------------------------

def _notify(
    *,
    event_key: str,
    recipient: Any,
    website: Any,
    context: dict,
    is_critical: bool = False,
) -> None:
    """Notify a single recipient. Never raises."""
    try:
        NotificationService.notify(
            event_key=event_key,
            recipient=recipient,
            website=website,
            context=context,
            is_critical=is_critical,
        )
    except Exception as exc:
        logger.exception(
            "_notify failed: event=%s recipient=%s: %s",
            event_key,
            getattr(recipient, "pk", "?"),
            exc,
        )


def _notify_role(
    *,
    event_key: str,
    role: str,
    website: Any,
    context: dict,
    is_critical: bool = False,
) -> None:
    """Notify all users of a role. Never raises."""
    try:
        NotificationService.notify_role(
            event_key=event_key,
            role=role,
            website=website,
            context=context,
            is_critical=is_critical,
        )
    except Exception as exc:
        logger.exception(
            "_notify_role failed: event=%s role=%s: %s",
            event_key,
            role,
            exc,
        )