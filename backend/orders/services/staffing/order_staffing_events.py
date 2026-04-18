from __future__ import annotations

from typing import Any, Optional

from orders.models import Order, OrderTimelineEvent
from orders.models.orders.constants import (
    ORDER_TIMELINE_EVENT_ASSIGNED,
    ORDER_TIMELINE_EVENT_INTEREST_CREATED,
    ORDER_TIMELINE_EVENT_INTEREST_WITHDRAWN,
    ORDER_TIMELINE_EVENT_POOL_OPENED,
    ORDER_TIMELINE_EVENT_PREFERRED_WRITER_DECLINED,
    ORDER_TIMELINE_EVENT_PREFERRED_WRITER_EXPIRED,
    ORDER_TIMELINE_EVENT_PREFERRED_WRITER_INVITED,
    ORDER_TIMELINE_EVENT_REASSIGNED,
    ORDER_TIMELINE_EVENT_RETURNED_TO_POOL,
)


class OrderStaffingEvents:
    """
    Own staffing timeline event creation.
    """

    @staticmethod
    def create(
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

    @classmethod
    def interest_created(
        cls,
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict,
    ) -> None:
        cls.create(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_INTEREST_CREATED,
            actor=actor,
            metadata=metadata,
        )

    @classmethod
    def interest_withdrawn(
        cls,
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict,
    ) -> None:
        cls.create(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_INTEREST_WITHDRAWN,
            actor=actor,
            metadata=metadata,
        )

    @classmethod
    def preferred_writer_invited(
        cls,
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict,
    ) -> None:
        cls.create(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_PREFERRED_WRITER_INVITED,
            actor=actor,
            metadata=metadata,
        )

    @classmethod
    def preferred_writer_declined(
        cls,
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict,
    ) -> None:
        cls.create(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_PREFERRED_WRITER_DECLINED,
            actor=actor,
            metadata=metadata,
        )

    @classmethod
    def preferred_writer_expired(
        cls,
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict,
    ) -> None:
        cls.create(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_PREFERRED_WRITER_EXPIRED,
            actor=actor,
            metadata=metadata,
        )

    @classmethod
    def pool_opened(
        cls,
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict,
    ) -> None:
        cls.create(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_POOL_OPENED,
            actor=actor,
            metadata=metadata,
        )

    @classmethod
    def assigned(
        cls,
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict,
    ) -> None:
        cls.create(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_ASSIGNED,
            actor=actor,
            metadata=metadata,
        )

    @classmethod
    def reassigned(
        cls,
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict,
    ) -> None:
        cls.create(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_REASSIGNED,
            actor=actor,
            metadata=metadata,
        )

    @classmethod
    def returned_to_pool(
        cls,
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict,
    ) -> None:
        cls.create(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_RETURNED_TO_POOL,
            actor=actor,
            metadata=metadata,
        )