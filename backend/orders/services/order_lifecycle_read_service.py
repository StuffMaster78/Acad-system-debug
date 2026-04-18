from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from django.db.models import QuerySet

from orders.models.adjustments.order_adjustment_request import (
    OrderAdjustmentRequest,
)
from orders.models.disputes.order_dispute import OrderDispute
from orders.models.orders.constants import (
    FREE_REVISION_WINDOW_DAYS,
    ORDER_STATUS_COMPLETED,
)
from orders.models.orders.order import Order
from orders.models.orders.order_assignment import OrderAssignment
from orders.models.orders.order_hold import OrderHold
from orders.models.orders.order_reassignment_request import (
    OrderReassignmentRequest,
)
from orders.models.revisions.order_revision_request import (
    OrderRevisionRequest,
)


@dataclass(frozen=True)
class OrderLifecycleSnapshot:
    """
    Represent a consolidated read side lifecycle snapshot for an order.
    """

    order_id: int
    order_status: str
    website_id: Optional[int]
    client_id: Optional[int]

    current_assignment_id: Optional[int]
    current_writer_id: Optional[int]
    has_current_assignment: bool

    active_hold_id: Optional[int]
    has_active_hold: bool

    pending_reassignment_request_id: Optional[int]
    has_pending_reassignment_request: bool

    active_dispute_id: Optional[int]
    has_active_dispute: bool

    latest_adjustment_request_id: Optional[int]
    latest_adjustment_status: Optional[str]

    latest_revision_request_id: Optional[int]
    latest_revision_status: Optional[str]

    is_revision_window_open: bool
    revision_window_days: int


class OrderLifecycleReadService:
    """
    Central read service for consolidated order lifecycle state.

    This service does not mutate state. It is designed to provide one
    dependable read model for dashboards, views, permissions, and policy
    checks that need a stitched order lifecycle snapshot.
    """

    ACTIVE_DISPUTE_STATUSES = frozenset({
        "open",
        "escalated",
        "resolved",
    })

    @classmethod
    def build_snapshot(
        cls,
        *,
        order: Order,
    ) -> OrderLifecycleSnapshot:
        """
        Build a consolidated lifecycle snapshot for a single order.
        """
        current_assignment = cls.get_current_assignment(order=order)
        active_hold = cls.get_active_hold(order=order)
        pending_reassignment = cls.get_pending_reassignment_request(
            order=order,
        )
        active_dispute = cls.get_active_dispute(order=order)
        latest_adjustment = cls.get_latest_adjustment_request(order=order)
        latest_revision = cls.get_latest_revision_request(order=order)

        return OrderLifecycleSnapshot(
            order_id=order.pk,
            order_status=order.status,
            website_id=cls._safe_fk_pk(order, "website"),
            client_id=cls._safe_fk_pk(order, "client"),
            current_assignment_id=(
                current_assignment.pk
                if current_assignment is not None
                else None
            ),
            current_writer_id=(
                cls._safe_fk_pk(current_assignment, "writer")
                if current_assignment is not None
                else None
            ),
            has_current_assignment=current_assignment is not None,
            active_hold_id=(
                active_hold.pk if active_hold is not None else None
            ),
            has_active_hold=active_hold is not None,
            pending_reassignment_request_id=(
                pending_reassignment.pk
                if pending_reassignment is not None
                else None
            ),
            has_pending_reassignment_request=(
                pending_reassignment is not None
            ),
            active_dispute_id=(
                active_dispute.pk if active_dispute is not None else None
            ),
            has_active_dispute=active_dispute is not None,
            latest_adjustment_request_id=(
                latest_adjustment.pk
                if latest_adjustment is not None
                else None
            ),
            latest_adjustment_status=(
                latest_adjustment.status
                if latest_adjustment is not None
                else None
            ),
            latest_revision_request_id=(
                latest_revision.pk
                if latest_revision is not None
                else None
            ),
            latest_revision_status=(
                latest_revision.status
                if latest_revision is not None
                else None
            ),
            is_revision_window_open=cls.is_revision_window_open(
                order=order,
            ),
            revision_window_days=FREE_REVISION_WINDOW_DAYS,
        )

    @classmethod
    def get_current_assignment(
        cls,
        *,
        order: Order,
    ) -> Optional[OrderAssignment]:
        """
        Return the current active assignment for the order.
        """
        return (
            OrderAssignment.objects.filter(
                order=order,
                is_current=True,
            )
            .select_related("writer")
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def get_active_hold(
        cls,
        *,
        order: Order,
    ) -> Optional[OrderHold]:
        """
        Return the currently active hold, if present.
        """
        return (
            OrderHold.objects.filter(
                order=order,
                status="active",
            )
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def get_pending_reassignment_request(
        cls,
        *,
        order: Order,
    ) -> Optional[OrderReassignmentRequest]:
        """
        Return the latest pending reassignment request, if present.
        """
        return (
            OrderReassignmentRequest.objects.filter(
                order=order,
                status="pending",
            )
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def get_active_dispute(
        cls,
        *,
        order: Order,
    ) -> Optional[OrderDispute]:
        """
        Return the latest active dispute, if present.
        """
        return (
            OrderDispute.objects.filter(
                order=order,
                status__in=cls.ACTIVE_DISPUTE_STATUSES,
            )
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def get_latest_adjustment_request(
        cls,
        *,
        order: Order,
    ) -> Optional[OrderAdjustmentRequest]:
        """
        Return the most recent adjustment request for the order.
        """
        return (
            OrderAdjustmentRequest.objects.filter(
                order=order,
            )
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def get_latest_revision_request(
        cls,
        *,
        order: Order,
    ) -> Optional[OrderRevisionRequest]:
        """
        Return the most recent revision request for the order.
        """
        return (
            OrderRevisionRequest.objects.filter(
                order=order,
            )
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def is_revision_window_open(
        cls,
        *,
        order: Order,
    ) -> bool:
        """
        Return whether the free revision window is still open.

        The window only applies to completed orders with completed_at.
        """
        completed_at = getattr(order, "completed_at", None)
        if order.status != ORDER_STATUS_COMPLETED:
            return False

        if completed_at is None:
            return False

        deadline = completed_at + cls._revision_window_delta()
        return cls._now() <= deadline

    @classmethod
    def visible_active_work_for_writer(
        cls,
        *,
        writer: Any,
    ) -> QuerySet[Order]:
        """
        Return active work orders currently assigned to the writer.
        """
        return (
            Order.objects.filter(
                website=writer.website,
                assignments__writer=writer,
                assignments__is_current=True,
            )
            .select_related(
                "website",
                "client",
                "preferred_writer",
            )
            .distinct()
        )

    @classmethod
    def visible_owned_orders_for_client(
        cls,
        *,
        client: Any,
    ) -> QuerySet[Order]:
        """
        Return orders owned by the client.
        """
        return Order.objects.filter(
            website=client.website,
            client=client,
        ).select_related(
            "website",
            "client",
            "preferred_writer",
        )

    @classmethod
    def visible_orders_for_staff(
        cls,
        *,
        staff_user: Any,
    ) -> QuerySet[Order]:
        """
        Return all tenant orders visible to staff.
        """
        return Order.objects.filter(
            website=staff_user.website,
        ).select_related(
            "website",
            "client",
            "preferred_writer",
        )

    @staticmethod
    def _safe_fk_pk(instance: Any, attr_name: str) -> Optional[int]:
        """
        Safely return a related object's primary key.
        """
        if instance is None:
            return None

        related_obj = getattr(instance, attr_name, None)
        if related_obj is None:
            return None

        return getattr(related_obj, "pk", None)

    @staticmethod
    def _now():
        """
        Indirection for current time to keep tests easy.
        """
        from django.utils import timezone

        return timezone.now()

    @staticmethod
    def _revision_window_delta():
        """
        Return the free revision time window.
        """
        from datetime import timedelta

        return timedelta(days=FREE_REVISION_WINDOW_DAYS)