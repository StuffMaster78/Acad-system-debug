"""
Own final submission, completion, and reopen workflow for orders.

WORKFLOW
--------
Writer IN_PROGRESS → submit_order()
        │
        ├─ requires_editing = True
        │       └─ UNDER_EDITING
        │               │ (auto-assign editor on commit)
        │         Editor reviews
        │               ├─ approved  → SUBMITTED → client
        │               └─ revision  → REVISION_REQUESTED → writer
        │
        ├─ requires_qa = True (and not editing)
        │       └─ QA_REVIEW
        │               │ (notify_staff on commit)
        │         Admin reviews
        │               ├─ approved  → SUBMITTED → client
        │               └─ returned  → IN_PROGRESS → writer
        │
        └─ neither → SUBMITTED → client directly

QA ACTOR
--------
Admin staff with can_handle_orders=True review QA orders.
GET /api/orders/?status=qa_review shows the queue.
notify_staff() alerts all active staff on the website on commit.

QA FIELDS (add to EditingRequirementConfig via migration)
----------------------------------------------------------
enable_qa_by_default         BooleanField(default=False)
qa_required_for_high_value   BooleanField(default=True)
qa_required_for_new_writers  BooleanField(default=True)
new_writer_order_threshold   PositiveIntegerField(default=5)

Until migration runs, getattr() defaults keep QA disabled safely.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.orders.order import Order
from orders.models.orders.order_assignment import OrderAssignment
from orders.models.orders.order_timeline_event import OrderTimelineEvent
from orders.models.orders.constants import (
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_SUBMITTED,
    ORDER_TIMELINE_EVENT_COMPLETED,
    ORDER_TIMELINE_EVENT_REOPENED,
    ORDER_TIMELINE_EVENT_SUBMITTED,
)
from orders.services.policies.order_status_transition_policy import (
    validate_status_transition,
)
from orders.models.orders.enums import OrderStatus
from orders.services.order_transition_service import OrderTransitionService

logger = logging.getLogger(__name__)

ORDER_STATUS_UNDER_EDITING = OrderStatus.UNDER_EDITING.value


class OrderSubmissionService:
    """
    Own final submission, completion, and reopen workflow for orders.
    """

    # ----------------------------------------------------------------
    # SUBMISSION — main entry point
    # ----------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def submit_order(
        cls,
        *,
        order: Order,
        submitted_by: Any,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Move an in-progress order forward after writer submission.

        Evaluates editing and QA policy in order:
            1. requires_editing → UNDER_EDITING + auto-assign editor
            2. requires_qa      → QA_REVIEW + notify staff
            3. neither          → SUBMITTED directly to client

        Args:
            order:        Order being submitted.
            submitted_by: Writer submitting the order.
            triggered_by: Optional actor performing the action.

        Returns:
            Updated Order.

        Raises:
            ValidationError: If order cannot be submitted.
        """
        locked_order = cls._lock_order(order)

        cls._ensure_can_submit(locked_order)
        cls._validate_actor_website(actor=submitted_by, order=locked_order)

        current_assignment = cls._get_current_assignment(locked_order)
        if current_assignment is None:
            raise ValidationError(
                "A current assignment is required for submission."
            )

        if current_assignment.writer != submitted_by:
            raise ValidationError(
                "Only the current assigned writer can submit the order."
            )

        if cls._requires_editing(locked_order):
            cls._route_to_editing(
                locked_order=locked_order,
                submitted_by=submitted_by,
                triggered_by=triggered_by,
            )
        elif cls._requires_qa(locked_order):
            cls._route_to_qa(
                locked_order=locked_order,
                submitted_by=submitted_by,
                triggered_by=triggered_by,
            )
        else:
            cls._route_to_client(
                locked_order=locked_order,
                submitted_by=submitted_by,
                triggered_by=triggered_by,
            )

        return locked_order

    # ----------------------------------------------------------------
    # ROUTING BRANCHES
    # ----------------------------------------------------------------

    @classmethod
    def _route_to_editing(
        cls,
        *,
        locked_order: Order,
        submitted_by: Any,
        triggered_by: Optional[Any],
    ) -> None:
        """
        Transition order to UNDER_EDITING and auto-assign editor on commit.
        """
        validate_status_transition(
            from_status=locked_order.status,
            to_status=ORDER_STATUS_UNDER_EDITING,
        )

        locked_order.status = ORDER_STATUS_UNDER_EDITING
        locked_order.submitted_at = timezone.now()
        locked_order.save(update_fields=[
            "status", "submitted_at", "updated_at",
        ])

        cls._create_timeline_event(
            order=locked_order,
            event_type="submitted_to_editing",
            actor=triggered_by or submitted_by,
            metadata={
                "submitted_by_id": getattr(submitted_by, "pk", None),
                "routed_to":       "editor",
            },
        )

        order_pk = locked_order.pk
        transaction.on_commit(
            lambda: _trigger_editor_assignment(order_pk)
        )

    @classmethod
    def _route_to_qa(
        cls,
        *,
        locked_order: Order,
        submitted_by: Any,
        triggered_by: Optional[Any],
    ) -> None:
        """
        Transition order to QA_REVIEW and notify all staff on commit.

        Staff are notified via NotificationService.notify_staff() which
        queries StaffWebsiteAssignment for all active staff on the website.
        The notification event key is: order.qa_review_ready

        Admin action URLs:
            Queue:   GET  /api/orders/?status=qa_review
            Approve: POST /api/orders/<pk>/qa/approve/
            Return:  POST /api/orders/<pk>/qa/return/
        """
        validate_status_transition(
            from_status=locked_order.status,
            to_status=OrderStatus.QA_REVIEW.value,
        )

        locked_order.status = OrderStatus.QA_REVIEW.value
        locked_order.submitted_at = timezone.now()
        locked_order.submitted_for_qa_at = timezone.now()
        locked_order.save(update_fields=[
            "status", "submitted_at", "submitted_for_qa_at", "updated_at",
        ])

        cls._create_timeline_event(
            order=locked_order,
            event_type="submitted_to_qa",
            actor=triggered_by or submitted_by,
            metadata={
                "submitted_by_id": getattr(submitted_by, "pk", None),
                "routed_to":       "qa",
            },
        )

        order_pk = locked_order.pk
        transaction.on_commit(
            lambda: _notify_qa_queue(order_pk)
        )

    @classmethod
    def _route_to_client(
        cls,
        *,
        locked_order: Order,
        submitted_by: Any,
        triggered_by: Optional[Any],
    ) -> None:
        """
        Transition order to SUBMITTED — direct delivery to client.
        No editing or QA required.
        """
        validate_status_transition(
            from_status=locked_order.status,
            to_status=ORDER_STATUS_SUBMITTED,
        )

        locked_order.status = ORDER_STATUS_SUBMITTED
        locked_order.submitted_at = timezone.now()
        locked_order.save(update_fields=[
            "status", "submitted_at", "updated_at",
        ])

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_SUBMITTED,
            actor=triggered_by or submitted_by,
            metadata={
                "submitted_by_id": getattr(submitted_by, "pk", None),
            },
        )
        cls._notify_submitted(
            order=locked_order,
            actor=triggered_by or submitted_by,
        )

    # ----------------------------------------------------------------
    # ADMIN BYPASS METHODS
    # ----------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def submit_directly_to_client(
        cls,
        *,
        order: Order,
        submitted_by: Any,
    ) -> Order:
        """
        Admin override — submit directly to client, skip all policy.
        Does not check editing or QA policy.
        """
        if order.status != OrderStatus.IN_PROGRESS.value:
            raise ValidationError(
                "Only in-progress orders can be submitted."
            )
        return OrderTransitionService.mark_submitted(
            order=order,
            actor=submitted_by,
        )

    @classmethod
    @transaction.atomic
    def submit_to_qa(
        cls,
        *,
        order: Order,
        submitted_by: Any,
    ) -> Order:
        """
        Admin override — force order into QA regardless of policy.
        """
        if order.status != OrderStatus.IN_PROGRESS.value:
            raise ValidationError(
                "Only in-progress orders can be submitted to QA."
            )
        return OrderTransitionService.mark_qa_review(
            order=order,
            actor=submitted_by,
        )

    # ----------------------------------------------------------------
    # COMPLETION
    # ----------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def complete_order(
        cls,
        *,
        order: Order,
        completed_by: Any,
        triggered_by: Optional[Any] = None,
        internal_reason: str = "",
    ) -> Order:
        """
        Move a submitted order to completed.

        Completion = submitted work operationally accepted.
        Unlocks downstream compensation logic.
        Approval is a separate post-completion milestone.
        """
        locked_order = cls._lock_order(order)

        cls._ensure_can_complete(locked_order)
        cls._validate_actor_website(actor=completed_by, order=locked_order)

        validate_status_transition(
            from_status=locked_order.status,
            to_status=ORDER_STATUS_COMPLETED,
        )

        locked_order.status = ORDER_STATUS_COMPLETED
        locked_order.completed_at = timezone.now()
        locked_order.save(update_fields=[
            "status", "completed_at", "updated_at",
        ])

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_COMPLETED,
            actor=triggered_by or completed_by,
            metadata={
                "completed_by_id": getattr(completed_by, "pk", None),
                "internal_reason": internal_reason,
                "completion_mode": "explicit",
            },
        )
        cls._notify_completed(
            order=locked_order,
            actor=triggered_by or completed_by,
        )
        return locked_order

    @classmethod
    @transaction.atomic
    def auto_complete_order(
        cls,
        *,
        order: Order,
        triggered_by: Optional[Any] = None,
        internal_reason: str = "auto_complete",
    ) -> Order:
        """Automatically complete a submitted order."""
        locked_order = cls._lock_order(order)

        cls._ensure_can_complete(locked_order)

        validate_status_transition(
            from_status=locked_order.status,
            to_status=ORDER_STATUS_COMPLETED,
        )

        locked_order.status = ORDER_STATUS_COMPLETED
        locked_order.completed_at = timezone.now()
        locked_order.save(update_fields=[
            "status", "completed_at", "updated_at",
        ])

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_COMPLETED,
            actor=triggered_by,
            metadata={
                "completed_by_id": None,
                "internal_reason": internal_reason,
                "completion_mode": "auto",
                "is_automatic":    True,
            },
        )
        cls._notify_completed(
            order=locked_order,
            actor=triggered_by,
        )
        return locked_order

    @classmethod
    @transaction.atomic
    def reopen_order(
        cls,
        *,
        order: Order,
        reopened_by: Any,
        reason: str,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """Reopen a completed order back to in-progress."""
        locked_order = cls._lock_order(order)

        cls._ensure_can_reopen(locked_order)
        cls._validate_actor_website(actor=reopened_by, order=locked_order)

        current_assignment = cls._get_current_assignment(locked_order)
        if current_assignment is None:
            raise ValidationError(
                "A current assignment is required to reopen the order."
            )

        validate_status_transition(
            from_status=locked_order.status,
            to_status=ORDER_STATUS_IN_PROGRESS,
        )

        locked_order.status = ORDER_STATUS_IN_PROGRESS
        locked_order.save(update_fields=["status", "updated_at"])

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_REOPENED,
            actor=triggered_by or reopened_by,
            metadata={
                "reopened_by_id": getattr(reopened_by, "pk", None),
                "reason":         reason,
            },
        )
        cls._notify_reopened(
            order=locked_order,
            actor=triggered_by or reopened_by,
            reason=reason,
        )
        return locked_order

    # ----------------------------------------------------------------
    # NOTIFICATION HELPERS
    # ----------------------------------------------------------------

    @staticmethod
    def _notify_submitted(*, order: Order, actor) -> None:
        try:
            from orders.services.order_notification_service import (
                OrderNotificationService,
            )
            OrderNotificationService.notify_order_submitted(
                order=order, submitted_by=actor
            )
        except Exception:
            logger.warning(
                "Failed to send submission notification for order_id=%s",
                getattr(order, "pk", None), exc_info=True,
            )

    @staticmethod
    def _notify_completed(*, order: Order, actor) -> None:
        try:
            from orders.services.order_notification_service import (
                OrderNotificationService,
            )
            OrderNotificationService.notify_order_completed(
                order=order, completed_by=actor
            )
        except Exception:
            logger.warning(
                "Failed to send completion notification for order_id=%s",
                getattr(order, "pk", None), exc_info=True,
            )

    @staticmethod
    def _notify_reopened(*, order: Order, actor, reason: str) -> None:
        try:
            from orders.services.order_notification_service import (
                OrderNotificationService,
            )
            OrderNotificationService.notify_order_reopened(
                order=order, reopened_by=actor, reason=reason
            )
        except Exception:
            logger.warning(
                "Failed to send reopen notification for order_id=%s",
                getattr(order, "pk", None), exc_info=True,
            )

    # ----------------------------------------------------------------
    # EDITING POLICY
    # ----------------------------------------------------------------

    @classmethod
    def _requires_editing(cls, order: Order) -> bool:
        """
        Resolve whether this order requires editor review before delivery.

        Resolution order:
            1. order.requires_editing flag (True/False — None = check policy)
            2. EditingRequirementConfig per website
            3. False (safe default)
        """
        if order.requires_editing is not None:
            return bool(order.requires_editing)

        try:
            from order_configs.models import EditingRequirementConfig
        except ImportError:
            logger.warning("_requires_editing: order_configs not available.")
            return False

        try:
            config = EditingRequirementConfig.objects.get(
                website=order.website
            )
            return cls._evaluate_editing_config(order=order, config=config)
        except EditingRequirementConfig.DoesNotExist:
            pass
        except Exception as exc:
            logger.exception(
                "_requires_editing: config read failed "
                "website=%s order=%s: %s",
                getattr(order.website, "pk", "?"),
                order.pk,
                exc,
            )

        return False

    @classmethod
    def _evaluate_editing_config(cls, *, order: Order, config: Any) -> bool:
        """Apply EditingRequirementConfig rules."""
        if not config.enable_editing_by_default:
            return False

        if config.skip_editing_for_urgent:
            if order.is_urgent:
                return False
            if order.client_deadline:
                hours_remaining = (
                    order.client_deadline - timezone.now()
                ).total_seconds() / 3600
                if hours_remaining < 24:
                    return False

        if (
            not config.allow_editing_for_early_submissions
            and order.client_deadline
        ):
            hours_remaining = (
                order.client_deadline - timezone.now()
            ).total_seconds() / 3600
            if hours_remaining > config.early_submission_hours_threshold:
                return False

        if config.editing_required_for_first_orders:
            if cls._is_first_client_order(order):
                return True

        if config.editing_required_for_high_value:
            threshold = Decimal(str(config.high_value_threshold))
            if order.total_price >= threshold:
                return True

        return True

    @classmethod
    def _is_first_client_order(cls, order: Order) -> bool:
        """Return True if this is the client's first delivered order."""
        if order.client is None:
            return False
        try:
            earliest_pk = (
                Order.objects.filter(
                    website=order.website,
                    client=order.client,
                    status__in=[
                        OrderStatus.SUBMITTED.value,
                        OrderStatus.COMPLETED.value,
                    ],
                )
                .order_by("pk")
                .values_list("pk", flat=True)
                .first()
            )
            if earliest_pk is None:
                return True
            return order.pk <= earliest_pk
        except Exception:
            return False

    # ----------------------------------------------------------------
    # QA POLICY
    # ----------------------------------------------------------------

    @classmethod
    def _requires_qa(cls, order: Order) -> bool:
        """
        Resolve whether this order requires QA before delivery.

        Only called when _requires_editing() returned False.
        One path only — editing OR QA, never both.

        Reads QA fields from EditingRequirementConfig via getattr()
        so this is safe to call before the migration adding those
        fields runs — all getattr() calls default to False/5.

        Returns True if any QA rule fires. False otherwise.
        """
        try:
            from order_configs.models import EditingRequirementConfig
        except ImportError:
            return False

        try:
            config = EditingRequirementConfig.objects.get(
                website=order.website
            )
        except EditingRequirementConfig.DoesNotExist:
            return False
        except Exception as exc:
            logger.exception(
                "_requires_qa: config read failed "
                "website=%s order=%s: %s",
                getattr(order.website, "pk", "?"),
                order.pk,
                exc,
            )
            return False

        # Global QA switch — opt-in, default off
        # getattr safe until migration adds the field
        if not getattr(config, "enable_qa_by_default", False):
            return False

        # Rule 1: high-value orders go to QA
        if getattr(config, "qa_required_for_high_value", False):
            threshold = Decimal(str(config.high_value_threshold))
            if order.total_price >= threshold:
                return True

        # Rule 2: new writer orders go to QA
        if getattr(config, "qa_required_for_new_writers", False):
            if cls._is_new_writer(order=order, config=config):
                return True

        return False

    @classmethod
    def _is_new_writer(cls, *, order: Order, config: Any) -> bool:
        """
        Return True if the assigned writer is below the experience threshold.

        A writer is 'new' if their count of delivered orders (SUBMITTED
        or COMPLETED) on this website is below new_writer_order_threshold.

        Uses OrderAssignment FK path for the count — order.assigned_writer
        is a @property and cannot be used in a queryset subquery.

        Returns False on any error — QA must not fire on ambiguity.

        Args:
            order:  The order being submitted.
            config: EditingRequirementConfig instance.

        Returns:
            True if writer is new and order should go to QA.
        """
        try:
            current_assignment = (
                OrderAssignment.objects.filter(
                    order=order,
                    is_current=True,
                )
                .select_related("writer")
                .first()
            )

            if current_assignment is None:
                logger.debug(
                    "_is_new_writer: no current assignment for order=%s",
                    order.pk,
                )
                return False

            writer = current_assignment.writer
            threshold: int = getattr(
                config, "new_writer_order_threshold", 5
            )

            delivered_count = Order.objects.filter(
                website=order.website,
                assignments__writer=writer,
                assignments__is_current=True,
                status__in=[
                    OrderStatus.SUBMITTED.value,
                    OrderStatus.COMPLETED.value,
                ],
            ).count()

            is_new = delivered_count < threshold

            logger.debug(
                "_is_new_writer: writer=%s delivered=%d threshold=%d "
                "is_new=%s order=%s",
                getattr(writer, "pk", "?"),
                delivered_count,
                threshold,
                is_new,
                order.pk,
            )

            return is_new

        except Exception as exc:
            logger.exception(
                "_is_new_writer: failed for order=%s: %s",
                order.pk,
                exc,
            )
            return False

    # ----------------------------------------------------------------
    # VALIDATION HELPERS
    # ----------------------------------------------------------------

    @classmethod
    def _ensure_can_submit(cls, order: Order) -> None:
        if order.status != ORDER_STATUS_IN_PROGRESS:
            raise ValidationError(
                "Only in-progress orders can be submitted."
            )

    @classmethod
    def _ensure_can_complete(cls, order: Order) -> None:
        if order.status != ORDER_STATUS_SUBMITTED:
            raise ValidationError(
                "Only submitted orders can be completed."
            )

    @classmethod
    def _ensure_can_reopen(cls, order: Order) -> None:
        if order.status != ORDER_STATUS_COMPLETED:
            raise ValidationError(
                "Only completed orders can be reopened."
            )

    @classmethod
    def _validate_actor_website(cls, *, actor: Any, order: Order) -> None:
        actor_website_id = getattr(actor, "website_id", None)
        if (
            actor_website_id is not None
            and actor_website_id != order.website.pk
        ):
            raise ValidationError(
                "Actor website must match order website."
            )

    @classmethod
    def _get_current_assignment(
        cls,
        order: Order,
    ) -> Optional[OrderAssignment]:
        return (
            OrderAssignment.objects.select_for_update()
            .filter(order=order, is_current=True)
            .select_related("writer")
            .first()
        )

    @classmethod
    def _lock_order(cls, order: Order) -> Order:
        return Order.objects.select_for_update().get(pk=order.pk)

    @classmethod
    def _create_timeline_event(
        cls,
        *,
        order: Order,
        event_type: str,
        actor: Optional[Any],
        metadata: dict,
    ) -> OrderTimelineEvent:
        return OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=event_type,
            actor=actor,
            metadata=metadata,
        )


# ----------------------------------------------------------------
# MODULE-LEVEL ON-COMMIT HELPERS
# ----------------------------------------------------------------

def _trigger_editor_assignment(order_pk: int) -> None:
    """
    Auto-assign editor after order moves to UNDER_EDITING.

    Called via transaction.on_commit — order row is fully committed
    and visible to the assignment service.

    Never raises — editor assignment failure must not roll back
    the writer's submission. Ops will be alerted via logging
    and can manually assign.
    """
    try:
        order = Order.objects.get(pk=order_pk)
        from editor_management.services.editor_assignment_service import (
            EditorAssignmentService,
        )
        EditorAssignmentService.auto_assign_order(order=order)
        logger.info(
            "_trigger_editor_assignment: editor assigned for order=%s",
            order_pk,
        )
    except Order.DoesNotExist:
        logger.error(
            "_trigger_editor_assignment: order=%s not found after commit.",
            order_pk,
        )
    except Exception as exc:
        logger.exception(
            "_trigger_editor_assignment: failed for order=%s: %s",
            order_pk,
            exc,
        )


def _notify_qa_queue(order_pk: int) -> None:
    """
    Notify all active staff when an order enters QA_REVIEW.

    Called via transaction.on_commit — order row is committed
    and the notification outbox can reference it safely.

    Uses NotificationService.notify_staff() which queries
    admin_management.StaffWebsiteAssignment for all active staff
    on the website and creates one outbox entry per person.

    Never raises — notification failure must not roll back
    the writer's submission.

    Notification event key:  order.qa_review_ready

    Context variables sent to template:
        order_id     int      — order PK
        order_topic  str      — topic truncated to 80 chars
        total_price  str      — decimal string e.g. "250.00"
        is_urgent    bool     — whether order is urgent
        writer_id    int|None — PK of the assigned writer

    Admin workflow after notification:
        View queue:  GET  /api/orders/?status=qa_review
        Approve:     POST /api/orders/<pk>/qa/approve/
        Return:      POST /api/orders/<pk>/qa/return/
    """
    try:
        order = Order.objects.select_related("website").get(pk=order_pk)

        # Resolve the assigned writer PK for context
        writer_id = None
        try:
            current = (
                OrderAssignment.objects
                .filter(order=order, is_current=True)
                .select_related("writer")
                .first()
            )
            if current:
                writer_id = getattr(current.writer, "pk", None)
        except Exception:
            pass

        from notifications_system.services.notification_service import (
            NotificationService,
        )
        NotificationService.notify_staff(
            event_key="order.qa_review_ready",
            website=order.website,
            context={
                "order_id":    order.pk,
                "order_topic": (order.topic or "")[:80],
                "total_price": str(order.total_price),
                "is_urgent":   order.is_urgent,
                "writer_id":   writer_id,
            },
        )

        logger.info(
            "_notify_qa_queue: staff notified for order=%s website=%s",
            order_pk,
            getattr(order.website, "pk", "?"),
        )

    except Order.DoesNotExist:
        logger.error(
            "_notify_qa_queue: order=%s not found after commit.",
            order_pk,
        )
    except Exception as exc:
        logger.exception(
            "_notify_qa_queue: failed for order=%s: %s",
            order_pk,
            exc,
        )