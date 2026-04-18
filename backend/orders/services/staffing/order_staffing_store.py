from __future__ import annotations

from typing import Any, Optional

from django.utils import timezone

from orders.models import Order, OrderAssignment, OrderInterest
from orders.models.orders.constants import (
    ORDER_ASSIGNMENT_STATUS_ACTIVE,
    ORDER_INTEREST_STATUS_PENDING,
)


class OrderStaffingStore:
    """
    Own staffing persistence helpers and locked ORM access.

    This class should stay boring:
    - locking
    - fetching
    - creating
    - bulk updates

    No business policy should live here.

    """

    @staticmethod
    def lock_order(order: Order) -> Order:
        """
        Lock and reload an order inside a transaction.
        """
        return Order.objects.select_for_update().get(pk=order.pk)

    @staticmethod
    def lock_interest(interest: OrderInterest) -> OrderInterest:
        """
        Lock and reload an interest inside a transaction.
        """
        return OrderInterest.objects.select_for_update().get(pk=interest.pk)

    @staticmethod
    def get_current_assignment(
        *,
        order: Order,
    ) -> Optional[OrderAssignment]:
        """
        Return the current active assignment for an order, if any.
        """
        return (
            OrderAssignment.objects.select_for_update()
            .filter(order=order, is_current=True)
            .select_related("writer")
            .first()
        )

    @staticmethod
    def get_pending_interest_for_writer(
        *,
        order: Order,
        writer: Any,
    ) -> Optional[OrderInterest]:
        """
        Return a pending interest for this writer and order, if any.
        """
        return (
            OrderInterest.objects.select_for_update()
            .filter(
                order=order,
                writer=writer,
                status=ORDER_INTEREST_STATUS_PENDING,
            )
            .first()
        )

    @staticmethod
    def get_pending_take_interest_for_writer_and_type(
        *,
        order: Order,
        writer: Any,
        interest_type: str,
    ) -> Optional[OrderInterest]:
        """
        Return a pending interest of a specific type for this writer/order.
        """
        return (
            OrderInterest.objects.select_for_update()
            .filter(
                order=order,
                writer=writer,
                interest_type=interest_type,
                status=ORDER_INTEREST_STATUS_PENDING,
            )
            .first()
        )

    @staticmethod
    def has_open_invitation_of_type(
        *,
        order: Order,
        interest_type: str,
    ) -> bool:
        """
        Return whether the order has an open pending invitation of a type.
        """
        return (
            OrderInterest.objects.select_for_update()
            .filter(
                order=order,
                interest_type=interest_type,
                status=ORDER_INTEREST_STATUS_PENDING,
            )
            .exists()
        )
    
    @staticmethod
    def create_interest(
        *,
        order: Order,
        writer: Any,
        interest_type: str,
        status: str,
        message: str = "",
        reviewed_by: Any = None,
        reviewed_at=None,
    ) -> OrderInterest:
        """
        Create an order interest record.
        """
        return OrderInterest.objects.create(
            website=order.website,
            order=order,
            writer=writer,
            interest_type=interest_type,
            status=status,
            message=message,
            reviewed_by=reviewed_by,
            reviewed_at=reviewed_at,
        )

    @staticmethod
    def create_assignment(
        *,
        order: Order,
        writer: Any,
        assigned_by: Any,
        source: str,
        source_interest: Optional[OrderInterest],
    ) -> OrderAssignment:
        """
        Create a new active current assignment.
        """
        return OrderAssignment.objects.create(
            website=order.website,
            order=order,
            writer=writer,
            assigned_by=assigned_by,
            source=source,
            status=ORDER_ASSIGNMENT_STATUS_ACTIVE,
            is_current=True,
            source_interest=source_interest,
        )

    @staticmethod
    def close_other_open_interests(
        *,
        order: Order,
        keep_interest: Optional[OrderInterest] = None,
        superseded_status: str,
    ) -> None:
        """
        Close competing pending interests after assignment.
        """
        queryset = OrderInterest.objects.select_for_update().filter(
            order=order,
            status=ORDER_INTEREST_STATUS_PENDING,
        )

        if keep_interest is not None:
            queryset = queryset.exclude(pk=keep_interest.pk)

        queryset.update(
            status=superseded_status,
            reviewed_at=timezone.now(),
        )