from __future__ import annotations

from datetime import timedelta
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models import Order, OrderTimelineEvent
from orders.models.orders.constants import (
    ORDER_STATUS_ARCHIVED,
    ORDER_STATUS_COMPLETED,
)


class OrderArchivalService:
    """
    Own explicit and automatic archival workflow for completed orders.

    Responsibilities:
        1. Archive completed orders after a retention window.
        2. Provide eligibility checks for archival.
        3. Record timeline history for archival actions.

    Notes:
        1. Archival is a lifecycle transition, so it belongs in orders.
        2. This service should not archive orders with unresolved work
           such as open disputes or pending reassignment requests. Those
           checks can be expanded later as the system matures.
    """

    AUTO_ARCHIVE_WINDOW_DAYS = 30
    TIMELINE_EVENT_ARCHIVED = "archived"

    @classmethod
    @transaction.atomic
    def archive_order(
        cls,
        *,
        order: Order,
        triggered_by=None,
    ) -> Order:
        """
        Explicitly archive an eligible order.

        Args:
            order:
                Order being archived.
            triggered_by:
                Optional actor or system marker.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the order cannot be archived.
        """
        locked_order = cls._lock_order(order)
        cls._ensure_can_archive(locked_order)

        archived_at = timezone.now()
        locked_order.archived_at = archived_at
        locked_order.status = ORDER_STATUS_ARCHIVED
        locked_order.save(
            update_fields=[
                "archived_at",
                "status",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=cls.TIMELINE_EVENT_ARCHIVED,
            actor=triggered_by,
            metadata={
                "archived_at": archived_at.isoformat(),
                "archive_mode": "explicit",
            },
        )
        return locked_order

    @classmethod
    @transaction.atomic
    def auto_archive_order(
        cls,
        *,
        order: Order,
        triggered_by=None,
    ) -> Order:
        """
        Automatically archive an eligible completed order.

        Args:
            order:
                Order being auto archived.
            triggered_by:
                Optional actor or system marker.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the order is not eligible for auto archival.
        """
        locked_order = cls._lock_order(order)
        cls._ensure_can_auto_archive(locked_order)

        archived_at = timezone.now()
        locked_order.archived_at = archived_at
        locked_order.status = ORDER_STATUS_ARCHIVED
        locked_order.save(
            update_fields=[
                "archived_at",
                "status",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=cls.TIMELINE_EVENT_ARCHIVED,
            actor=triggered_by,
            metadata={
                "archived_at": archived_at.isoformat(),
                "archive_mode": "auto",
            },
        )
        return locked_order

    @classmethod
    def can_auto_archive(
        cls,
        *,
        order: Order,
    ) -> bool:
        """
        Return whether the order is eligible for automatic archival.

        Args:
            order:
                Order being evaluated.

        Returns:
            bool:
                True when the order may be auto archived.
        """
        if order.status != ORDER_STATUS_COMPLETED:
            return False

        if getattr(order, "archived_at", None) is not None:
            return False

        completed_at = getattr(order, "completed_at", None)
        if completed_at is None:
            return False

        archive_after = completed_at + timedelta(
            days=cls.AUTO_ARCHIVE_WINDOW_DAYS
        )
        return timezone.now() >= archive_after

    @classmethod
    def _ensure_can_archive(
        cls,
        order: Order,
    ) -> None:
        """
        Ensure the order may be explicitly archived.

        Args:
            order:
                Order being validated.

        Raises:
            ValidationError:
                Raised when the order cannot be archived.
        """
        if order.status != ORDER_STATUS_COMPLETED:
            raise ValidationError(
                "Only completed orders can be archived."
            )

        if getattr(order, "archived_at", None) is not None:
            raise ValidationError(
                "Order has already been archived."
            )

    @classmethod
    def _ensure_can_auto_archive(
        cls,
        order: Order,
    ) -> None:
        """
        Ensure the order may be automatically archived.

        Args:
            order:
                Order being validated.

        Raises:
            ValidationError:
                Raised when auto archival is invalid.
        """
        if not cls.can_auto_archive(order=order):
            raise ValidationError(
                "Order is not eligible for automatic archival."
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
        actor,
        metadata: dict,
    ) -> OrderTimelineEvent:
        """
        Create a timeline event for archival activity.

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