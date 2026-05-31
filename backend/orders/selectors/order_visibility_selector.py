from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import Q, QuerySet

# FK fields accessed by OrderListSerializer on every list response.
# Bundled into one constant so all selectors stay in sync.
ORDER_LIST_SELECT_RELATED = (
    "client",
    "assigned_writer",
    "preferred_writer",
    "website",
    "paper_type",
    "subject",
    "academic_level",
)

from orders.models import OrderInterest
from orders.models.orders.constants import (
    ORDER_INTEREST_STATUS_ACCEPTED,
    ORDER_INTEREST_STATUS_PENDING,
    ORDER_PAYMENT_STATUS_FULLY_PAID,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_ON_HOLD,
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_STATUS_SUBMITTED,
    ORDER_VISIBILITY_POOL,
    ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
)
from orders.models.orders.order import Order
from writer_management.utils import get_writer_profile


@dataclass(frozen=True)
class OrderVisibilitySnapshot:
    """Represent why an order is visible to an actor."""

    can_view: bool
    visibility_reason: str
    is_pool_visible: bool
    is_preferred_writer_visible: bool
    is_current_assignment_visible: bool
    is_client_visible: bool
    is_staff_visible: bool


class OrderVisibilitySelector:
    """Central read layer for order visibility rules."""

    WRITER_ACTIVE_WORK_STATUSES = frozenset({
        ORDER_STATUS_IN_PROGRESS,
        ORDER_STATUS_ON_HOLD,
        ORDER_STATUS_SUBMITTED,
    })
    OPEN_INTEREST_STATUSES = frozenset({
        ORDER_INTEREST_STATUS_PENDING,
        ORDER_INTEREST_STATUS_ACCEPTED,
    })

    @classmethod
    def visible_to_client(cls, *, client: Any) -> QuerySet[Order]:
        """Return orders visible to a client."""
        website = cls._website_for_user(client)
        queryset = Order.objects.select_related(*ORDER_LIST_SELECT_RELATED).filter(client=client)
        if website is not None:
            queryset = queryset.filter(website=website)
        return queryset

    @classmethod
    def visible_to_staff(cls, *, staff_user: Any) -> QuerySet[Order]:
        """Return all tenant orders visible to staff."""
        website = cls._website_for_user(staff_user)
        queryset = Order.objects.select_related(*ORDER_LIST_SELECT_RELATED).all()
        if website is not None:
            queryset = queryset.filter(website=website)
        return queryset

    @classmethod
    def visible_to_writer(cls, *, writer: Any) -> QuerySet[Order]:
        """Return all orders visible to a writer."""
        website = cls._website_for_user(writer)
        writer_profile = get_writer_profile(writer)
        if website is None or writer_profile is None:
            return Order.objects.none()

        return Order.objects.select_related(*ORDER_LIST_SELECT_RELATED).filter(
            website=website
        ).filter(
            cls._writer_visibility_q(
                writer=writer,
                writer_profile=writer_profile,
            )
        ).distinct()

    @classmethod
    def pool_visible_to_writer(cls, *, writer: Any) -> QuerySet[Order]:
        """Return staffing-ready pool orders visible to a writer."""
        website = cls._website_for_user(writer)
        if website is None:
            return Order.objects.none()
        return Order.objects.filter(
            website=website,
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
            payment_status=ORDER_PAYMENT_STATUS_FULLY_PAID,
        )

    @classmethod
    def preferred_writer_visible_to_writer(
        cls,
        *,
        writer: Any,
    ) -> QuerySet[Order]:
        """Return preferred-writer-only orders visible to a writer."""
        website = cls._website_for_user(writer)
        if website is None:
            return Order.objects.none()
        return Order.objects.filter(
            website=website,
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer=writer,
            payment_status=ORDER_PAYMENT_STATUS_FULLY_PAID,
        )

    @classmethod
    def assigned_to_writer(cls, *, writer: Any) -> QuerySet[Order]:
        """Return orders currently assigned to the writer."""
        website = cls._website_for_user(writer)
        writer_profile = get_writer_profile(writer)
        if website is None or writer_profile is None:
            return Order.objects.none()
        return Order.objects.filter(
            website=website,
            status__in=cls.WRITER_ACTIVE_WORK_STATUSES,
            assignments__writer=writer_profile,
            assignments__is_current=True,
        ).distinct()

    @classmethod
    def requested_by_writer(cls, *, writer: Any) -> QuerySet[Order]:
        """Return orders with active writer staffing interests."""
        website = cls._website_for_user(writer)
        if website is None:
            return Order.objects.none()
        return Order.objects.filter(
            website=website,
            interests__writer=writer,
            interests__status__in=cls.OPEN_INTEREST_STATUSES,
        ).distinct()

    @classmethod
    def requested_order_ids_for_writer(cls, *, writer: Any) -> QuerySet:
        """Return order IDs with active writer interests."""
        return cls.requested_by_writer(writer=writer).values_list(
            "id",
            flat=True,
        )

    @classmethod
    def pending_interest_count_for_writer(cls, *, writer: Any) -> int:
        """Count pending staffing interests for a writer."""
        website = cls._website_for_user(writer)
        if website is None:
            return 0
        return OrderInterest.objects.filter(
            website=website,
            writer=writer,
            status=ORDER_INTEREST_STATUS_PENDING,
        ).count()

    @classmethod
    def can_writer_view_order(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> OrderVisibilitySnapshot:
        """Return a structured visibility snapshot for a writer and order."""
        writer_website = cls._website_for_user(writer)
        writer_website_pk = getattr(writer_website, "pk", None)
        writer_profile = get_writer_profile(writer)

        if getattr(order, "website_id", None) != writer_website_pk:
            return cls._snapshot(False, "cross_tenant_blocked")

        is_pool_visible = cls._is_pool_visible_to_writer(
            writer=writer,
            order=order,
        )
        is_preferred_visible = cls._is_preferred_writer_visible_to_writer(
            writer=writer,
            order=order,
        )
        is_assignment_visible = cls._is_current_assignment_visible_to_writer(
            writer=writer,
            writer_profile=writer_profile,
            order=order,
        )
        is_interest_visible = cls._has_open_interest(
            writer=writer,
            order=order,
        )

        can_view = (
            is_pool_visible
            or is_preferred_visible
            or is_assignment_visible
            or is_interest_visible
        )
        reason = "not_visible"
        if is_interest_visible:
            reason = "active_interest"
        elif is_assignment_visible:
            reason = "current_assignment"
        elif is_preferred_visible:
            reason = "preferred_writer_invitation"
        elif is_pool_visible:
            reason = "pool_visible"

        return OrderVisibilitySnapshot(
            can_view=can_view,
            visibility_reason=reason,
            is_pool_visible=is_pool_visible,
            is_preferred_writer_visible=is_preferred_visible,
            is_current_assignment_visible=is_assignment_visible,
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
        """Return a structured visibility snapshot for a client and order."""
        can_view = (
            getattr(order, "client_id", None) == getattr(client, "pk", None)
            and getattr(order, "website_id", None)
            == getattr(cls._website_for_user(client), "pk", None)
        )
        return OrderVisibilitySnapshot(
            can_view=can_view,
            visibility_reason="order_owner" if can_view else "not_order_owner",
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
        """Return a structured visibility snapshot for staff and order."""
        can_view = (
            getattr(order, "website_id", None)
            == getattr(cls._website_for_user(staff_user), "pk", None)
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
    def _writer_visibility_q(cls, *, writer: Any, writer_profile: Any) -> Q:
        """Build the combined visibility query for a writer."""
        return (
            Q(
                status=ORDER_STATUS_READY_FOR_STAFFING,
                visibility_mode=ORDER_VISIBILITY_POOL,
                payment_status=ORDER_PAYMENT_STATUS_FULLY_PAID,
            )
            | Q(
                status=ORDER_STATUS_READY_FOR_STAFFING,
                visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
                preferred_writer=writer,
                payment_status=ORDER_PAYMENT_STATUS_FULLY_PAID,
            )
            | Q(
                status__in=cls.WRITER_ACTIVE_WORK_STATUSES,
                assignments__writer=writer_profile,
                assignments__is_current=True,
            )
            | Q(
                interests__writer=writer,
                interests__status__in=cls.OPEN_INTEREST_STATUSES,
            )
        )

    @classmethod
    def _is_pool_visible_to_writer(cls, *, writer: Any, order: Order) -> bool:
        """Return whether the order is visible in the public writer pool."""
        return (
            getattr(order, "website_id", None)
            == getattr(cls._website_for_user(writer), "pk", None)
            and order.status == ORDER_STATUS_READY_FOR_STAFFING
            and order.visibility_mode == ORDER_VISIBILITY_POOL
            and cls._is_paid(order)
        )

    @classmethod
    def _is_preferred_writer_visible_to_writer(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> bool:
        """Return whether the order is visible to the invited writer."""
        return (
            getattr(order, "website_id", None)
            == getattr(cls._website_for_user(writer), "pk", None)
            and order.status == ORDER_STATUS_READY_FOR_STAFFING
            and order.visibility_mode
            == ORDER_VISIBILITY_PREFERRED_WRITER_ONLY
            and getattr(order, "preferred_writer_id", None)
            == getattr(writer, "pk", None)
            and cls._is_paid(order)
        )

    @classmethod
    def _is_current_assignment_visible_to_writer(
        cls,
        *,
        writer: Any,
        writer_profile: Any,
        order: Order,
    ) -> bool:
        """Return whether the order is visible because it is assigned."""
        if (
            getattr(order, "website_id", None)
            != getattr(cls._website_for_user(writer), "pk", None)
        ):
            return False
        if writer_profile is None:
            return False
        if order.status not in cls.WRITER_ACTIVE_WORK_STATUSES:
            return False

        current_assignments = getattr(order, "assignments", None)
        if current_assignments is None:
            return False
        return current_assignments.filter(
            writer=writer_profile,
            is_current=True,
        ).exists()

    @classmethod
    def _has_open_interest(cls, *, writer: Any, order: Order) -> bool:
        """Return whether the writer has an active staffing interest."""
        if (
            getattr(order, "website_id", None)
            != getattr(cls._website_for_user(writer), "pk", None)
        ):
            return False
        if not cls._is_paid(order):
            return False

        interests = getattr(order, "interests", None)
        if interests is None:
            return False
        return interests.filter(
            writer=writer,
            status__in=cls.OPEN_INTEREST_STATUSES,
        ).exists()

    @staticmethod
    def _website_for_user(user: Any) -> Any:
        """Resolve a user's active tenant website."""
        website = getattr(user, "website", None)
        if website is not None:
            return website

        try:
            profile = (
                user.account_profiles
                .select_related("website")
                .filter(is_primary=True)
                .first()
            )
            if profile is not None:
                return profile.website
        except Exception:
            return None

        return None

    @staticmethod
    def _is_paid(order: Order) -> bool:
        """Return whether an order is sufficiently paid for visibility."""
        if getattr(order, "is_paid", False):
            return True
        if getattr(order, "payment_status", None) == ORDER_PAYMENT_STATUS_FULLY_PAID:
            return True
        try:
            return order.amount_paid >= order.total_price
        except Exception:
            return False

    @staticmethod
    def _snapshot(can_view: bool, reason: str) -> OrderVisibilitySnapshot:
        """Build an empty structured visibility snapshot."""
        return OrderVisibilitySnapshot(
            can_view=can_view,
            visibility_reason=reason,
            is_pool_visible=False,
            is_preferred_writer_visible=False,
            is_current_assignment_visible=False,
            is_client_visible=False,
            is_staff_visible=False,
        )
