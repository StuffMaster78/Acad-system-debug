from __future__ import annotations

from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.orders.order import Order
from orders.models.orders.order_hold import OrderHold
from orders.models.orders.order_timeline_event import OrderTimelineEvent
from orders.models.orders.constants import (
    ORDER_HOLD_STATUS_ACTIVE,
    ORDER_HOLD_STATUS_CANCELLED,
    ORDER_HOLD_STATUS_PENDING,
    ORDER_HOLD_STATUS_RELEASED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_ON_HOLD,
    ORDER_TIMELINE_EVENT_HOLD_ACTIVATED,
    ORDER_TIMELINE_EVENT_HOLD_RELEASED,
    ORDER_TIMELINE_EVENT_HOLD_REQUESTED,
)


class OrderHoldService:
    """
    Own hold request, activation, and release workflow for orders.
    """

    @classmethod
    @transaction.atomic
    def request_hold(
        cls,
        *,
        order: Order,
        requested_by: Any,
        reason: str,
        internal_notes: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderHold:
        """
        Create a pending hold request for an order.
        """
        locked_order = cls._lock_order(order)

        cls._ensure_can_request_hold(locked_order)
        cls._ensure_no_open_hold(locked_order)
        cls._validate_actor_website(actor=requested_by, order=locked_order)

        hold = OrderHold.objects.create(
            website=locked_order.website,
            order=locked_order,
            requested_by=requested_by,
            status=ORDER_HOLD_STATUS_PENDING,
            reason=reason,
            internal_notes=internal_notes,
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_HOLD_REQUESTED,
            actor=triggered_by or requested_by,
            metadata={
                "hold_id": hold.pk,
                "requested_by_id": getattr(requested_by, "pk", None),
                "reason": reason,
            },
        )
        return hold

    @classmethod
    @transaction.atomic
    def activate_hold(
        cls,
        *,
        hold: OrderHold,
        activated_by: Any,
        remaining_seconds: int,
        internal_notes: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderHold:
        """
        Activate a pending hold and place the order on hold.
        """
        locked_hold = cls._lock_hold(hold)
        locked_order = cls._lock_order(locked_hold.order)

        cls._ensure_pending_hold(locked_hold)
        cls._validate_actor_website(actor=activated_by, order=locked_order)

        if remaining_seconds < 0:
            raise ValidationError(
                "remaining_seconds cannot be negative."
            )

        locked_hold.status = ORDER_HOLD_STATUS_ACTIVE
        locked_hold.placed_by = activated_by
        locked_hold.placed_at = timezone.now()
        locked_hold.remaining_seconds = remaining_seconds
        if internal_notes:
            locked_hold.internal_notes = internal_notes
        locked_hold.save(
            update_fields=[
                "status",
                "placed_by",
                "placed_at",
                "remaining_seconds",
                "internal_notes",
                "updated_at",
            ]
        )

        locked_order.status = ORDER_STATUS_ON_HOLD
        locked_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_HOLD_ACTIVATED,
            actor=triggered_by or activated_by,
            metadata={
                "hold_id": locked_hold.pk,
                "activated_by_id": getattr(activated_by, "pk", None),
                "remaining_seconds": remaining_seconds,
            },
        )
        return locked_hold

    @classmethod
    @transaction.atomic
    def release_hold(
        cls,
        *,
        hold: OrderHold,
        released_by: Any,
        internal_notes: str = "",
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Release an active hold and return the order to in progress.
        """
        locked_hold = cls._lock_hold(hold)
        locked_order = cls._lock_order(locked_hold.order)

        cls._ensure_active_hold(locked_hold)
        cls._validate_actor_website(actor=released_by, order=locked_order)

        locked_hold.status = ORDER_HOLD_STATUS_RELEASED
        locked_hold.released_by = released_by
        locked_hold.released_at = timezone.now()
        if internal_notes:
            locked_hold.internal_notes = internal_notes
        locked_hold.save(
            update_fields=[
                "status",
                "released_by",
                "released_at",
                "internal_notes",
                "updated_at",
            ]
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
            event_type=ORDER_TIMELINE_EVENT_HOLD_RELEASED,
            actor=triggered_by or released_by,
            metadata={
                "hold_id": locked_hold.pk,
                "released_by_id": getattr(released_by, "pk", None),
                "remaining_seconds": locked_hold.remaining_seconds,
            },
        )
        return locked_order

    @classmethod
    @transaction.atomic
    def cancel_hold_request(
        cls,
        *,
        hold: OrderHold,
        cancelled_by: Any,
        internal_notes: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderHold:
        """
        Cancel a pending hold request.
        """
        locked_hold = cls._lock_hold(hold)

        cls._ensure_pending_hold(locked_hold)

        if locked_hold.requested_by != cancelled_by:
            raise ValidationError(
                "Only the requester can cancel this hold request."
            )

        locked_hold.status = ORDER_HOLD_STATUS_CANCELLED
        locked_hold.cancelled_at = timezone.now()
        if internal_notes:
            locked_hold.internal_notes = internal_notes
        locked_hold.save(
            update_fields=[
                "status",
                "cancelled_at",
                "internal_notes",
                "updated_at",
            ]
        )

        return locked_hold

    @classmethod
    def _ensure_can_request_hold(cls, order: Order) -> None:
        """
        Ensure the order can enter hold request flow.
        """
        if order.status != ORDER_STATUS_IN_PROGRESS:
            raise ValidationError(
                "Only in progress orders can request hold."
            )

    @classmethod
    def _ensure_no_open_hold(cls, order: Order) -> None:
        """
        Ensure the order has no pending or active hold.
        """
        open_hold_exists = (
            OrderHold.objects.select_for_update()
            .filter(
                order=order,
                status__in=[
                    ORDER_HOLD_STATUS_PENDING,
                    ORDER_HOLD_STATUS_ACTIVE,
                ],
            )
            .exists()
        )
        if open_hold_exists:
            raise ValidationError(
                "Order already has an open hold request."
            )

    @classmethod
    def _ensure_pending_hold(cls, hold: OrderHold) -> None:
        """
        Ensure hold is pending.
        """
        if hold.status != ORDER_HOLD_STATUS_PENDING:
            raise ValidationError(
                "Only pending hold requests can be reviewed."
            )

    @classmethod
    def _ensure_active_hold(cls, hold: OrderHold) -> None:
        """
        Ensure hold is active.
        """
        if hold.status != ORDER_HOLD_STATUS_ACTIVE:
            raise ValidationError(
                "Only active holds can be released."
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
    def _lock_order(cls, order: Order) -> Order:
        """
        Lock and reload an order inside a transaction.
        """
        return Order.objects.select_for_update().get(pk=order.pk)

    @classmethod
    def _lock_hold(cls, hold: OrderHold) -> OrderHold:
        """
        Lock and reload a hold inside a transaction.
        """
        return OrderHold.objects.select_for_update().get(pk=hold.pk)

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
        Create a timeline event for hold workflow changes.
        """
        return OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=event_type,
            actor=actor,
            metadata=metadata,
        )