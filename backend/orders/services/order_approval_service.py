from __future__ import annotations

from datetime import timedelta
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.orders.order import Order
from orders.models.orders.order_timeline_event import (
    OrderTimelineEvent,
)
from orders.models.orders.constants import (
    FREE_REVISION_WINDOW_DAYS,
    ORDER_STATUS_COMPLETED,
    ORDER_TIMELINE_EVENT_APPROVED,
)


class OrderApprovalService:
    """
    Own explicit and automatic order approval workflow.

    Responsibilities:
        1. Explicit client or staff approval of completed work.
        2. Automatic approval after the configured approval window.
        3. Timeline event creation for approval milestones.

    Approval is a post-completion milestone.
    Reviews, ratings, and tips can happen after approval.
    """

    AUTO_APPROVAL_WINDOW_DAYS = FREE_REVISION_WINDOW_DAYS

    @classmethod
    @transaction.atomic
    def approve_order(
        cls,
        *,
        order: Order,
        approved_by: Any,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Explicitly approve a completed order.

        Args:
            order:
                Order being approved.
            approved_by:
                Actor approving the order.
            triggered_by:
                Optional actor recorded on downstream events.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the order cannot be approved.
        """
        locked_order = cls._lock_order(order)
        cls._ensure_can_be_approved(locked_order)

        approved_at = timezone.now()
        locked_order.approved_at = approved_at
    
        locked_order.save(
            update_fields=[
                "approved_at",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_APPROVED,
            actor=triggered_by or approved_by,
            metadata={
                "approved_by_id": getattr(approved_by, "pk", None),
                "approval_mode": "explicit",
                "approved_at": approved_at.isoformat(),
                "completed_at": (
                    locked_order.completed_at.isoformat()
                    if locked_order.completed_at is not None
                    else None
                ),
            },
        )
        return locked_order

    @classmethod
    @transaction.atomic
    def auto_approve_order(
        cls,
        *,
        order: Order,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Automatically approve a completed order
        after the approval window expires.

        Args:
            order:
                Order being auto approved.
            triggered_by:
                Optional actor or system marker for timeline events.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the order is not eligible for auto approval.
        """
        locked_order = cls._lock_order(order)
        cls._ensure_can_auto_approve(locked_order)

        approved_at = timezone.now()
        locked_order.approved_at = approved_at

        locked_order.save(
            update_fields=[
                "approved_at",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_APPROVED,
            actor=triggered_by,
            metadata={
                "approval_mode": "auto",
                "approved_at": approved_at.isoformat(),
                   "completed_at": (
                        locked_order.completed_at.isoformat()
                        if locked_order.completed_at is not None
                        else None
                    ),
            },
        )
        return locked_order

    @classmethod
    def can_auto_approve(cls, *, order: Order) -> bool:
        """
        Return whether the order is eligible for automatic approval.

        Args:
            order:
                Order being evaluated.

        Returns:
            bool:
                True when the order can be auto approved.
        """
        if order.status != ORDER_STATUS_COMPLETED:
            return False

        if getattr(order, "approved_at", None) is not None:
            return False

        completed_at = getattr(order, "completed_at", None)
        if completed_at is None:
            return False

        deadline = completed_at + timedelta(
            days=cls.AUTO_APPROVAL_WINDOW_DAYS
        )
        return timezone.now() >= deadline

    @classmethod
    def _ensure_can_be_approved(cls, order: Order) -> None:
        """
        Ensure the order is eligible for explicit approval.

        Args:
            order:
                Order being validated.

        Raises:
            ValidationError:
                Raised when approval is invalid.
        """    
        if order.status != ORDER_STATUS_COMPLETED:
            raise ValidationError(
                "You can only approve a completed order."
            )
        
        if getattr(order, "completed_at", None) is None:
            raise ValidationError(
                "Completed orders must have completed_at."
            )

        if getattr(order, "approved_at", None) is not None:
            raise ValidationError(
                "Order has already been approved."
            )

    @classmethod
    def _ensure_can_auto_approve(cls, order: Order) -> None:
        """
        Ensure the order is eligible for auto approval.

        Args:
            order:
                Order being validated.

        Raises:
            ValidationError:
                Raised when auto approval is invalid.
        """
        if not cls.can_auto_approve(order=order):
            raise ValidationError(
                "Order is not eligible for automatic approval."
            )

    @staticmethod
    def _lock_order(order: Order) -> Order:
        """
        Lock and reload an order inside a transaction.

        Args:
            order:
                Order to lock.

        Returns:
            Order:
                Locked order.
        """
        return Order.objects.select_for_update().get(pk=order.pk)

    @staticmethod
    def _create_timeline_event(
        *,
        order: Order,
        event_type: str,
        actor: Optional[Any],
        metadata: dict[str, Any],
    ) -> OrderTimelineEvent:
        """
        Create an order timeline event.

        Args:
            order:
                Order receiving the event.
            event_type:
                Timeline event type.
            actor:
                Optional actor linked to the event.
            metadata:
                Structured metadata payload.

        Returns:
            OrderTimelineEvent:
                Created timeline event.
        """
        return OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=event_type,
            actor=actor,
            metadata=metadata,
        )