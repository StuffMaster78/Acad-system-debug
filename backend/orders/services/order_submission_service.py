from __future__ import annotations

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
from orders.services.order_transition_service import (
    OrderTransitionService,
)

class OrderSubmissionService:
    """
    Own final submission, completion, and reopen workflow for orders.
    """

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
        Move an in progress order to submitted.

        Args:
            order:
                Order being submitted.
            submitted_by:
                Writer submitting the order.
            triggered_by:
                Optional actor performing the action.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the order cannot be submitted.
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
        
        validate_status_transition(
            from_status=locked_order.status,
            to_status=ORDER_STATUS_SUBMITTED,
        )

        locked_order.status = ORDER_STATUS_SUBMITTED
        locked_order.submitted_at = timezone.now()
        locked_order.save(
            update_fields=[
                "status",
                "submitted_at",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_SUBMITTED,
            actor=triggered_by or submitted_by,
            metadata={
                "submitted_by_id": getattr(submitted_by, "pk", None),
            },
        )
        return locked_order
    @classmethod
    @transaction.atomic
    def submit_directly_to_client(
        cls,
        *,
        order,
        submitted_by,
    ):
        """
        Submit order directly to client when QA is not required.
        """
        if order.status != OrderStatus.IN_PROGRESS:
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
        order,
        submitted_by,
    ):
        """
        Submit order to QA review.
        """
        if order.status != OrderStatus.IN_PROGRESS:
            raise ValidationError(
                "Only in-progress orders can be submitted to QA."
            )

        return OrderTransitionService.mark_qa_review(
            order=order,
            actor=submitted_by,
        )
    
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

        Completion means the submitted work is
        operationally accepted as okay.
        It may be triggered by client, staff,
        or approved automation rules.
        Completion unlocks downstream compensation logic.

        Approval is a separate post-completion milestone.

        Args:
            order:
                Submitted order.
            completed_by:
                Actor completing the order.
            triggered_by:
                Optional actor performing the action.
            internal_reason:
                Optional internal reason for completion.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the order cannot be completed.
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
        locked_order.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

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
        """
        Automatically complete a submitted order.

        Args:
            order:
                Submitted order.
            triggered_by:
                Optional actor performing the action.
            internal_reason:
                Internal reason for automatic completion.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the order cannot be auto completed.
        """
        locked_order = cls._lock_order(order)

        cls._ensure_can_complete(locked_order)

        validate_status_transition(
            from_status=locked_order.status,
            to_status=ORDER_STATUS_COMPLETED,
        )

        locked_order.status = ORDER_STATUS_COMPLETED
        locked_order.completed_at = timezone.now()
        locked_order.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_COMPLETED,
            actor=triggered_by,
            metadata={
                "completed_by_id": None,
                "internal_reason": internal_reason,
                "completion_mode": "auto",
                "is_automatic": True,
            },
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
        """
        Reopen a completed order back to in progress.

        Args:
            order:
                Completed order.
            reopened_by:
                Staff actor reopening the order.
            reason:
                Reason for reopening.
            triggered_by:
                Optional actor performing the action.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the order cannot be reopened.
        """
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
        locked_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_REOPENED,
            actor=triggered_by or reopened_by,
            metadata={
                "reopened_by_id": getattr(reopened_by, "pk", None),
                "reason": reason,
            },
        )
        return locked_order

    @classmethod
    def _ensure_can_submit(cls, order: Order) -> None:
        """
        Ensure the order can be submitted.
        """
        if order.status != ORDER_STATUS_IN_PROGRESS:
            raise ValidationError(
                "Only in progress orders can be submitted."
            )

    @classmethod
    def _ensure_can_complete(cls, order: Order) -> None:
        """
        Ensure the order can be completed.
        """
        if order.status != ORDER_STATUS_SUBMITTED:
            raise ValidationError(
                "Only submitted orders can be completed."
            )

    @classmethod
    def _ensure_can_reopen(cls, order: Order) -> None:
        """
        Ensure the order can be reopened.
        """
        if order.status != ORDER_STATUS_COMPLETED:
            raise ValidationError(
                "Only completed orders can be reopened."
            )

    @classmethod
    def _validate_actor_website(
        cls,
        *,
        actor: Any,
        order: Order,
    ) -> None:
        """
        Ensure actor belongs to the same tenant as the order.
        """
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
        """
        Return the current active assignment for an order.
        """
        return (
            OrderAssignment.objects.select_for_update()
            .filter(order=order, is_current=True)
            .select_related("writer")
            .first()
        )

    @classmethod
    def _lock_order(cls, order: Order) -> Order:
        """
        Lock and reload an order inside a transaction.
        """
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
        """
        Create a timeline event for submission workflow changes.
        """
        return OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=event_type,
            actor=actor,
            metadata=metadata,
        )