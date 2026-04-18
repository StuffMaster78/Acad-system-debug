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
class WriterEligibilitySnapshot:
    """
    Represent whether a writer can interact with an order and why.
    """

    can_bid: bool
    can_take: bool
    can_view_pool: bool
    can_view_preferred_invite: bool
    has_capacity: bool
    is_same_tenant: bool
    is_preferred_writer: bool
    is_order_staffing_ready: bool
    is_pool_visible: bool
    is_preferred_writer_visible: bool
    reason: str


class WriterEligibilitySelector:
    """
    Central read layer for writer order eligibility.

    This selector only answers read side questions.
    It does not mutate state, assign orders, or create requests.
    """

    ACTIVE_WORK_STATUSES = frozenset({
        ORDER_STATUS_IN_PROGRESS,
        ORDER_STATUS_ON_HOLD,
        ORDER_STATUS_SUBMITTED,
    })

    @classmethod
    def active_orders_for_writer(
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
                status__in=cls.ACTIVE_WORK_STATUSES,
                assignments__writer=writer,
                assignments__is_current=True,
            )
            .distinct()
        )

    @classmethod
    def available_pool_orders_for_writer(
        cls,
        *,
        writer: Any,
    ) -> QuerySet[Order]:
        """
        Return staffing ready pool visible orders for the writer.
        """
        return Order.objects.filter(
            website=writer.website,
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
        )

    @classmethod
    def preferred_writer_orders_for_writer(
        cls,
        *,
        writer: Any,
    ) -> QuerySet[Order]:
        """
        Return preferred writer invitation orders visible to the writer.
        """
        return Order.objects.filter(
            website=writer.website,
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer=writer,
        )

    @classmethod
    def eligible_orders_for_writer(
        cls,
        *,
        writer: Any,
    ) -> QuerySet[Order]:
        """
        Return orders a writer is allowed to interact with.

        This includes:
            1. Pool visible staffing ready orders
            2. Preferred writer invitation orders
        """
        return (
            Order.objects.filter(
                website=writer.website,
            )
            .filter(
                Q(
                    status=ORDER_STATUS_READY_FOR_STAFFING,
                    visibility_mode=ORDER_VISIBILITY_POOL,
                )
                | Q(
                    status=ORDER_STATUS_READY_FOR_STAFFING,
                    visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
                    preferred_writer=writer,
                )
            )
            .distinct()
        )

    @classmethod
    def build_snapshot(
        cls,
        *,
        writer: Any,
        order: Order,
        active_order_count: int,
        max_active_orders: int,
        takes_enabled: bool,
        bidding_enabled: bool,
        ignore_capacity_for_preferred_writer: bool = True,
    ) -> WriterEligibilitySnapshot:
        """
        Build a structured writer eligibility snapshot for an order.

        Args:
            writer:
                Writer being evaluated.
            order:
                Target order.
            active_order_count:
                Current number of active orders assigned to the writer.
            max_active_orders:
                Maximum active orders allowed for the writer.
            takes_enabled:
                Whether direct self take is enabled for the writer.
            bidding_enabled:
                Whether bidding or interest submission is enabled.
            ignore_capacity_for_preferred_writer:
                Whether preferred writer routing bypasses normal capacity.

        Returns:
            WriterEligibilitySnapshot:
                Structured read model describing writer eligibility.
        """
        is_same_tenant = cls._is_same_tenant(writer=writer, order=order)
        is_order_staffing_ready = (
            order.status == ORDER_STATUS_READY_FOR_STAFFING
        )
        is_pool_visible = (
            order.visibility_mode == ORDER_VISIBILITY_POOL
        )
        is_preferred_writer_visible = (
            order.visibility_mode == ORDER_VISIBILITY_PREFERRED_WRITER_ONLY
        )
        is_preferred_writer = cls._is_preferred_writer(
            writer=writer,
            order=order,
        )
        has_capacity = active_order_count < max_active_orders

        can_view_pool = (
            is_same_tenant
            and is_order_staffing_ready
            and is_pool_visible
        )

        can_view_preferred_invite = (
            is_same_tenant
            and is_order_staffing_ready
            and is_preferred_writer_visible
            and is_preferred_writer
        )

        preferred_writer_capacity_ok = (
            has_capacity
            or (
                ignore_capacity_for_preferred_writer
                and can_view_preferred_invite
            )
        )

        can_bid = (
            bidding_enabled
            and preferred_writer_capacity_ok
            and (
                can_view_pool
                or can_view_preferred_invite
            )
        )

        can_take = (
            takes_enabled
            and preferred_writer_capacity_ok
            and can_view_pool
        )

        reason = cls._build_reason(
            is_same_tenant=is_same_tenant,
            is_order_staffing_ready=is_order_staffing_ready,
            is_pool_visible=is_pool_visible,
            is_preferred_writer_visible=is_preferred_writer_visible,
            is_preferred_writer=is_preferred_writer,
            has_capacity=has_capacity,
            takes_enabled=takes_enabled,
            bidding_enabled=bidding_enabled,
            can_view_pool=can_view_pool,
            can_view_preferred_invite=can_view_preferred_invite,
            can_bid=can_bid,
            can_take=can_take,
            ignore_capacity_for_preferred_writer=(
                ignore_capacity_for_preferred_writer
            ),
        )

        return WriterEligibilitySnapshot(
            can_bid=can_bid,
            can_take=can_take,
            can_view_pool=can_view_pool,
            can_view_preferred_invite=can_view_preferred_invite,
            has_capacity=has_capacity,
            is_same_tenant=is_same_tenant,
            is_preferred_writer=is_preferred_writer,
            is_order_staffing_ready=is_order_staffing_ready,
            is_pool_visible=is_pool_visible,
            is_preferred_writer_visible=is_preferred_writer_visible,
            reason=reason,
        )

    @classmethod
    def _build_reason(
        cls,
        *,
        is_same_tenant: bool,
        is_order_staffing_ready: bool,
        is_pool_visible: bool,
        is_preferred_writer_visible: bool,
        is_preferred_writer: bool,
        has_capacity: bool,
        takes_enabled: bool,
        bidding_enabled: bool,
        can_view_pool: bool,
        can_view_preferred_invite: bool,
        can_bid: bool,
        can_take: bool,
        ignore_capacity_for_preferred_writer: bool,
    ) -> str:
        """
        Build a single dominant reason for the eligibility outcome.
        """
        if not is_same_tenant:
            return "cross_tenant_blocked"

        if not is_order_staffing_ready:
            return "order_not_staffing_ready"

        if is_preferred_writer_visible and not is_preferred_writer:
            return "preferred_writer_only"

        if not can_view_pool and not can_view_preferred_invite:
            return "not_visible_to_writer"

        if not has_capacity:
            if (
                ignore_capacity_for_preferred_writer
                and can_view_preferred_invite
            ):
                return "preferred_writer_capacity_override"
            return "writer_at_capacity"

        if can_take:
            return "eligible_for_take"

        if can_bid:
            return "eligible_for_bid"

        if can_view_pool and not bidding_enabled and not takes_enabled:
            return "writer_actions_disabled"

        if can_view_preferred_invite and not bidding_enabled:
            return "preferred_writer_visible_but_actions_disabled"

        if can_view_pool and not takes_enabled:
            return "take_disabled"

        if can_view_pool and not bidding_enabled:
            return "bidding_disabled"

        return "not_eligible"

    @classmethod
    def _is_same_tenant(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> bool:
        """
        Return whether the writer and order belong to the same tenant.
        """
        order_website_pk = (
            order.website.pk
            if getattr(order, "website", None) is not None
            else None
        )
        writer_website_pk = getattr(writer, "website_id", None)
        return order_website_pk == writer_website_pk

    @classmethod
    def _is_preferred_writer(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> bool:
        """
        Return whether the writer is the preferred writer on the order.
        """
        preferred_writer = getattr(order, "preferred_writer", None)
        if preferred_writer is None:
            return False
        return getattr(preferred_writer, "pk", None) == getattr(
            writer,
            "pk",
            None,
        )