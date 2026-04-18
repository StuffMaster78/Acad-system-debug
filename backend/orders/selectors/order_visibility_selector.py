from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import Q, QuerySet

from orders.models.orders.constants import (
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_ON_HOLD,
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_STATUS_SUBMITTED,
    ORDER_VISIBILITY_POOL,
    ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
)
from orders.models.orders.order import Order


@dataclass(frozen=True)
class OrderVisibilitySnapshot:
    """
    Represent why an order is visible to an actor.
    """

    can_view: bool
    visibility_reason: str
    is_pool_visible: bool
    is_preferred_writer_visible: bool
    is_current_assignment_visible: bool
    is_client_visible: bool
    is_staff_visible: bool


class OrderVisibilitySelector:
    """
    Central read layer for order visibility rules.

    This selector does not mutate state. It only answers who can see
    what order and why.
    """

    WRITER_ACTIVE_WORK_STATUSES = frozenset({
        ORDER_STATUS_IN_PROGRESS,
        ORDER_STATUS_ON_HOLD,
        ORDER_STATUS_SUBMITTED,
    })

    @classmethod
    def visible_to_client(
        cls,
        *,
        client: Any,
    ) -> QuerySet[Order]:
        """
        Return orders visible to a client.
        """
        return Order.objects.filter(
            client=client,
            website=client.website,
        )

    @classmethod
    def visible_to_staff(
        cls,
        *,
        staff_user: Any,
    ) -> QuerySet[Order]:
        """
        Return all tenant orders visible to staff.

        Staff visibility is tenant wide.
        """
        return Order.objects.filter(
            website=staff_user.website,
        )

    @classmethod
    def visible_to_writer(
        cls,
        *,
        writer: Any,
    ) -> QuerySet[Order]:
        """
        Return all orders visible to a writer across visibility buckets.

        Includes:
            1. Pool visible staffing ready orders
            2. Preferred writer only orders for that writer
            3. Currently assigned active work
        """
        website = writer.website

        return (
            Order.objects.filter(
                website=website,
            )
            .filter(
                cls._writer_visibility_q(writer=writer)
            )
            .distinct()
        )

    @classmethod
    def pool_visible_to_writer(
        cls,
        *,
        writer: Any,
    ) -> QuerySet[Order]:
        """
        Return staffing ready pool visible orders for a writer.
        """
        return Order.objects.filter(
            website=writer.website,
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
        )

    @classmethod
    def preferred_writer_visible_to_writer(
        cls,
        *,
        writer: Any,
    ) -> QuerySet[Order]:
        """
        Return preferred writer only orders visible to the invited writer.
        """
        return Order.objects.filter(
            website=writer.website,
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer=writer,
        )

    @classmethod
    def assigned_to_writer(
        cls,
        *,
        writer: Any,
    ) -> QuerySet[Order]:
        """
        Return orders currently assigned to the writer.
        """
        return (
            Order.objects.filter(
                website=writer.website,
                status__in=cls.WRITER_ACTIVE_WORK_STATUSES,
                assignments__writer=writer,
                assignments__is_current=True,
            )
            .distinct()
        )

    @classmethod
    def can_writer_view_order(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> OrderVisibilitySnapshot:
        """
        Return a structured visibility snapshot for a writer and order.
        """
        order_website_pk = (
            order.website.pk
            if getattr(order, "website", None) is not None
            else None
        )
        writer_website_pk = getattr(writer, "website_id", None)

        if order_website_pk != writer_website_pk:
            return OrderVisibilitySnapshot(
                can_view=False,
                visibility_reason="cross_tenant_blocked",
                is_pool_visible=False,
                is_preferred_writer_visible=False,
                is_current_assignment_visible=False,
                is_client_visible=False,
                is_staff_visible=False,
            )

        is_pool_visible = cls._is_pool_visible_to_writer(
            writer=writer,
            order=order,
        )
        is_preferred_writer_visible = (
            cls._is_preferred_writer_visible_to_writer(
                writer=writer,
                order=order,
            )
        )
        is_current_assignment_visible = (
            cls._is_current_assignment_visible_to_writer(
                writer=writer,
                order=order,
            )
        )

        can_view = (
            is_pool_visible
            or is_preferred_writer_visible
            or is_current_assignment_visible
        )

        if is_current_assignment_visible:
            visibility_reason = "current_assignment"
        elif is_preferred_writer_visible:
            visibility_reason = "preferred_writer_invitation"
        elif is_pool_visible:
            visibility_reason = "pool_visible"
        else:
            visibility_reason = "not_visible"

        return OrderVisibilitySnapshot(
            can_view=can_view,
            visibility_reason=visibility_reason,
            is_pool_visible=is_pool_visible,
            is_preferred_writer_visible=is_preferred_writer_visible,
            is_current_assignment_visible=is_current_assignment_visible,
            is_client_visible=False,
            is_staff_visible=False,
        )

    @classmethod
    def can_client_view_order(
        cls,
        *,
        client: Any,
        order: Order,
    ) -> OrderVisibilitySnapshot:
        """
        Return a structured visibility snapshot for a client and order.
        """
        can_view = (
            getattr(order, "client_id", None) == getattr(client, "pk", None)
            and getattr(order, "website_id", None)
            == getattr(client, "website_id", None)
        )

        return OrderVisibilitySnapshot(
            can_view=can_view,
            visibility_reason=(
                "order_owner" if can_view else "not_order_owner"
            ),
            is_pool_visible=False,
            is_preferred_writer_visible=False,
            is_current_assignment_visible=False,
            is_client_visible=can_view,
            is_staff_visible=False,
        )

    @classmethod
    def can_staff_view_order(
        cls,
        *,
        staff_user: Any,
        order: Order,
    ) -> OrderVisibilitySnapshot:
        """
        Return a structured visibility snapshot for staff and order.
        """
        can_view = (
            getattr(order, "website_id", None)
            == getattr(staff_user, "website_id", None)
        )

        return OrderVisibilitySnapshot(
            can_view=can_view,
            visibility_reason=(
                "tenant_staff_access" if can_view else "cross_tenant_blocked"
            ),
            is_pool_visible=False,
            is_preferred_writer_visible=False,
            is_current_assignment_visible=False,
            is_client_visible=False,
            is_staff_visible=can_view,
        )

    @classmethod
    def _writer_visibility_q(cls, *, writer: Any) -> Q:
        """
        Build the combined visibility query for a writer.
        """
        return (
            Q(
                status=ORDER_STATUS_READY_FOR_STAFFING,
                visibility_mode=ORDER_VISIBILITY_POOL,
            )
            | Q(
                status=ORDER_STATUS_READY_FOR_STAFFING,
                visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
                preferred_writer=writer,
            )
            | Q(
                status__in=cls.WRITER_ACTIVE_WORK_STATUSES,
                assignments__writer=writer,
                assignments__is_current=True,
            )
        )

    @classmethod
    def _is_pool_visible_to_writer(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> bool:
        """
        Return whether the order is visible in the public writer pool.
        """
        return (
            getattr(order, "website_id", None) == getattr(writer, "website_id", None)
            and order.status == ORDER_STATUS_READY_FOR_STAFFING
            and order.visibility_mode == ORDER_VISIBILITY_POOL
        )

    @classmethod
    def _is_preferred_writer_visible_to_writer(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> bool:
        """
        Return whether the order is visible to the invited preferred writer.
        """
        return (
            getattr(order, "website_id", None) == getattr(writer, "website_id", None)
            and order.status == ORDER_STATUS_READY_FOR_STAFFING
            and order.visibility_mode
            == ORDER_VISIBILITY_PREFERRED_WRITER_ONLY
            and getattr(order, "preferred_writer_id", None)
            == getattr(writer, "pk", None)
        )

    @classmethod
    def _is_current_assignment_visible_to_writer(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> bool:
        """
        Return whether the order is visible because it is currently assigned.
        """
        if (
            getattr(order, "website_id", None)
            != getattr(writer, "website_id", None)
        ):
            return False

        if order.status not in cls.WRITER_ACTIVE_WORK_STATUSES:
            return False

        current_assignments = getattr(order, "assignments", None)
        if current_assignments is None:
            return False

        return current_assignments.filter(
            writer=writer,
            is_current=True,
        ).exists()