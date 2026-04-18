from __future__ import annotations

from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models import Order, OrderTimelineEvent
from orders.models.orders.constants import ORDER_STATUS_IN_PROGRESS


class OrderEngagementService:
    """
    Own lightweight engagement signals tied to order execution.

    Responsibilities:
        1. Record when a writer acknowledges active work.
        2. Provide simple eligibility checks for acknowledgements.

    This service records trust and engagement signals.
    It does not replace the messaging app.
    """

    TIMELINE_EVENT_WRITER_ACKNOWLEDGED = "writer_acknowledged"

    @classmethod
    @transaction.atomic
    def acknowledge_order(
        cls,
        *,
        order: Order,
        writer: Any,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Record that the current writer has acknowledged the order.

        Args:
            order:
                Order being acknowledged.
            writer:
                Writer acknowledging the order.
            triggered_by:
                Optional actor recorded on timeline event.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the order cannot be acknowledged.
        """
        locked_order = cls._lock_order(order)
        cls._ensure_can_acknowledge(locked_order)

        acknowledged_at = timezone.now()
        locked_order.last_writer_acknowledged_at = acknowledged_at
        locked_order.save(
            update_fields=[
                "last_writer_acknowledged_at",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=cls.TIMELINE_EVENT_WRITER_ACKNOWLEDGED,
            actor=triggered_by or writer,
            metadata={
                "writer_id": getattr(writer, "pk", None),
                "acknowledged_at": acknowledged_at.isoformat(),
            },
        )
        return locked_order

    @staticmethod
    def can_acknowledge(
        *,
        order: Order,
    ) -> bool:
        """
        Return whether an order is eligible for acknowledgement.

        Args:
            order:
                Order being evaluated.

        Returns:
            bool:
                True when acknowledgement is allowed.
        """
        return order.status == ORDER_STATUS_IN_PROGRESS

    @classmethod
    def _ensure_can_acknowledge(
        cls,
        order: Order,
    ) -> None:
        """
        Ensure acknowledgement is valid for the order.

        Args:
            order:
                Order being validated.

        Raises:
            ValidationError:
                Raised when acknowledgement is invalid.
        """
        if not cls.can_acknowledge(order=order):
            raise ValidationError(
                "Only in progress orders can be acknowledged."
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
        Create a timeline event for engagement activity.

        Args:
            order:
                Order receiving the event.
            event_type:
                Timeline event type.
            actor:
                Optional actor linked to the event.
            metadata:
                Structured event metadata.

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