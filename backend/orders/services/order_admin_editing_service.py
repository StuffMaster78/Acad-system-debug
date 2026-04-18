from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction

from orders.models import Order, OrderTimelineEvent
from orders.services.order_flagging_service import OrderFlaggingService


class OrderAdminEditingService:
    """
    Own controlled staff and admin edits to order fields.

    Responsibilities:
        1. Update sensitive order fields through explicit methods.
        2. Recompute operational flags when relevant fields change.
        3. Record timeline history for operational traceability.

    This service should be used instead of random serializer or view
    updates for sensitive fields such as deadlines, price, and pages.
    """

    TIMELINE_EVENT_ORDER_EDITED = "order_edited"

    @classmethod
    @transaction.atomic
    def update_deadline(
        cls,
        *,
        order: Order,
        new_writer_deadline,
        edited_by: Any,
        reason: str,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Update the writer deadline for an order.

        Args:
            order:
                Order being edited.
            new_writer_deadline:
                New writer deadline.
            edited_by:
                Staff actor making the change.
            reason:
                Operational reason for the change.
            triggered_by:
                Optional actor for timeline logging.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the new deadline is invalid.
        """
        locked_order = cls._lock_order(order)

        if new_writer_deadline is None:
            raise ValidationError(
                "new_writer_deadline is required."
            )

        old_deadline = getattr(locked_order, "writer_deadline", None)
        locked_order.writer_deadline = new_writer_deadline
        locked_order.save(
            update_fields=[
                "writer_deadline",
                "updated_at",
            ]
        )

        OrderFlaggingService.refresh_flags(order=locked_order)

        cls._create_timeline_event(
            order=locked_order,
            actor=triggered_by or edited_by,
            metadata={
                "field": "writer_deadline",
                "old_value": (
                    old_deadline.isoformat()
                    if old_deadline is not None
                    else None
                ),
                "new_value": new_writer_deadline.isoformat(),
                "reason": reason,
                "edited_by_id": getattr(edited_by, "pk", None),
            },
        )
        return locked_order

    @classmethod
    @transaction.atomic
    def update_total_price(
        cls,
        *,
        order: Order,
        new_total_price: Decimal,
        edited_by: Any,
        reason: str,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Update the commercial total price for an order.

        Args:
            order:
                Order being edited.
            new_total_price:
                New total price.
            edited_by:
                Staff actor making the edit.
            reason:
                Operational reason for the change.
            triggered_by:
                Optional actor for timeline logging.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the price is invalid.
        """
        locked_order = cls._lock_order(order)

        if new_total_price < Decimal("0.00"):
            raise ValidationError(
                "new_total_price cannot be negative."
            )

        old_total_price = getattr(locked_order, "total_price", None)
        locked_order.total_price = new_total_price
        locked_order.save(
            update_fields=[
                "total_price",
                "updated_at",
            ]
        )

        OrderFlaggingService.refresh_flags(order=locked_order)

        cls._create_timeline_event(
            order=locked_order,
            actor=triggered_by or edited_by,
            metadata={
                "field": "total_price",
                "old_value": str(old_total_price),
                "new_value": str(new_total_price),
                "reason": reason,
                "edited_by_id": getattr(edited_by, "pk", None),
            },
        )
        return locked_order

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
        actor: Optional[Any],
        metadata: dict[str, Any],
    ) -> OrderTimelineEvent:
        """
        Create an order edited timeline event.

        Args:
            order:
                Order receiving the event.
            actor:
                Actor performing the edit.
            metadata:
                Structured timeline metadata.

        Returns:
            OrderTimelineEvent:
                Created timeline event.
        """
        return OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=OrderAdminEditingService.TIMELINE_EVENT_ORDER_EDITED,
            actor=actor,
            metadata=metadata,
        )