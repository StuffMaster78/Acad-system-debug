from __future__ import annotations

from typing import Any, Optional

from django.db import transaction
from django.utils import timezone

from orders.models import Order, OrderAssignment, OrderInterest
from orders.models.orders.constants import (
    ORDER_ASSIGNMENT_SOURCE_ACCEPTED_INTEREST,
    ORDER_ASSIGNMENT_SOURCE_PREFERRED_WRITER_ACCEPTANCE,
    ORDER_ASSIGNMENT_SOURCE_SELF_TAKE,
    ORDER_ASSIGNMENT_SOURCE_STAFF_ASSIGNMENT,
    ORDER_ASSIGNMENT_STATUS_RELEASED,
    ORDER_INTEREST_STATUS_ACCEPTED,
    ORDER_INTEREST_STATUS_DECLINED,
    ORDER_INTEREST_STATUS_EXPIRED,
    ORDER_INTEREST_STATUS_PENDING,
    ORDER_INTEREST_STATUS_SUPERSEDED,
    ORDER_INTEREST_STATUS_WITHDRAWN,
    ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION,
    ORDER_INTEREST_TYPE_REQUEST_TAKE,
    ORDER_INTEREST_TYPE_SHOW_INTEREST,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_VISIBILITY_HIDDEN,
    ORDER_VISIBILITY_POOL,
    ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
    PREFERRED_WRITER_STATUS_ACCEPTED,
    PREFERRED_WRITER_STATUS_DECLINED,
    PREFERRED_WRITER_STATUS_EXPIRED,
    PREFERRED_WRITER_STATUS_FALLBACK_TO_POOL,
    PREFERRED_WRITER_STATUS_INVITED,
    PREFERRED_WRITER_STATUS_NOT_REQUESTED,
    ORDER_STATUS_READY_FOR_STAFFING,
)
from orders.services.staffing.order_staffing_events import (
    OrderStaffingEvents,
)
from orders.services.staffing.order_staffing_policy import (
    OrderStaffingPolicy,
)
from orders.services.staffing.order_staffing_store import (
    OrderStaffingStore,
)


class OrderStaffingService:
    """
    Own staffing visibility and assignment workflow for orders.
    """

    @classmethod
    @transaction.atomic
    def route_order_to_staffing(
        cls,
        *,
        order: Order,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        locked_order = OrderStaffingStore.lock_order(order)
        current_assignment = OrderStaffingStore.get_current_assignment(
            order=locked_order
        )

        OrderStaffingPolicy.validate_can_route_order(
            order=locked_order,
            has_current_assignment=current_assignment is not None,
        )

        if locked_order.preferred_writer is not None:
            return cls._invite_preferred_writer(
                order=locked_order,
                triggered_by=triggered_by,
            )

        return cls._open_order_to_pool(
            order=locked_order,
            triggered_by=triggered_by,
        )

    @classmethod
    @transaction.atomic
    def express_interest(
        cls,
        *,
        order: Order,
        writer: Any,
        message: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderInterest:
        locked_order = OrderStaffingStore.lock_order(order)
        current_assignment = OrderStaffingStore.get_current_assignment(
            order=locked_order
        )
        existing_interest = OrderStaffingStore.get_pending_interest_for_writer(
            order=locked_order,
            writer=writer,
        )

        OrderStaffingPolicy.validate_can_express_interest(
            order=locked_order,
            writer=writer,
            has_current_assignment=current_assignment is not None,
            has_pending_interest=existing_interest is not None,
        )

        interest = OrderInterest.objects.create(
            website=locked_order.website,
            order=locked_order,
            writer=writer,
            interest_type=ORDER_INTEREST_TYPE_SHOW_INTEREST,
            status=ORDER_INTEREST_STATUS_PENDING,
            message=message,
        )

        OrderStaffingEvents.interest_created(
            order=locked_order,
            actor=triggered_by or writer,
            metadata={
                "interest_id": interest.pk,
                "writer_id": getattr(writer, "pk", None),
            },
        )
        return interest

    @classmethod
    @transaction.atomic
    def withdraw_interest(
        cls,
        *,
        interest: OrderInterest,
        writer: Any,
        triggered_by: Optional[Any] = None,
    ) -> OrderInterest:
        locked_interest = OrderStaffingStore.lock_interest(interest)

        OrderStaffingPolicy.validate_can_withdraw_interest(
            interest=locked_interest,
            writer=writer,
        )

        locked_interest.status = ORDER_INTEREST_STATUS_WITHDRAWN
        locked_interest.withdrawn_at = timezone.now()
        locked_interest.save(
            update_fields=[
                "status",
                "withdrawn_at",
                "updated_at",
            ]
        )

        OrderStaffingEvents.interest_withdrawn(
            order=locked_interest.order,
            actor=triggered_by or writer,
            metadata={
                "interest_id": locked_interest.pk,
                "writer_id": getattr(writer, "pk", None),
                "action": "withdraw_interest",
            },
        )
        return locked_interest

    @classmethod
    @transaction.atomic
    def take_order(
        cls,
        *,
        order: Order,
        writer: Any,
        triggered_by: Optional[Any] = None,
    ) -> OrderAssignment:
        locked_order = OrderStaffingStore.lock_order(order)
        current_assignment = OrderStaffingStore.get_current_assignment(
            order=locked_order
        )

        OrderStaffingPolicy.validate_can_take_order(
            order=locked_order,
            writer=writer,
            has_current_assignment=current_assignment is not None,
        )

        existing_interest = (
            OrderStaffingStore.get_pending_take_interest_for_writer_and_type(
                order=locked_order,
                writer=writer,
                interest_type=ORDER_INTEREST_TYPE_REQUEST_TAKE,
            )
        )

        if existing_interest is None:
            existing_interest = OrderInterest.objects.create(
                website=locked_order.website,
                order=locked_order,
                writer=writer,
                interest_type=ORDER_INTEREST_TYPE_REQUEST_TAKE,
                status=ORDER_INTEREST_STATUS_ACCEPTED,
                reviewed_by=triggered_by or writer,
                reviewed_at=timezone.now(),
            )
        else:
            existing_interest.status = ORDER_INTEREST_STATUS_ACCEPTED
            existing_interest.reviewed_by = triggered_by or writer
            existing_interest.reviewed_at = timezone.now()
            existing_interest.save(
                update_fields=[
                    "status",
                    "reviewed_by",
                    "reviewed_at",
                    "updated_at",
                ]
            )

        assignment = OrderStaffingStore.create_assignment(
            order=locked_order,
            writer=writer,
            assigned_by=triggered_by or writer,
            source=ORDER_ASSIGNMENT_SOURCE_SELF_TAKE,
            source_interest=existing_interest,
        )

        OrderStaffingStore.close_other_open_interests(
            order=locked_order,
            keep_interest=existing_interest,
            superseded_status=ORDER_INTEREST_STATUS_SUPERSEDED,
        )
        cls._mark_order_in_progress(
            order=locked_order,
            actor=triggered_by or writer,
            metadata={
                "assignment_id": assignment.pk,
                "writer_id": getattr(writer, "pk", None),
                "source": ORDER_ASSIGNMENT_SOURCE_SELF_TAKE,
            },
        )
        return assignment

    @classmethod
    @transaction.atomic
    def assign_from_interest(
        cls,
        *,
        interest: OrderInterest,
        assigned_by: Any,
    ) -> OrderAssignment:
        locked_interest = OrderStaffingStore.lock_interest(interest)
        locked_order = OrderStaffingStore.lock_order(locked_interest.order)
        current_assignment = OrderStaffingStore.get_current_assignment(
            order=locked_order
        )

        OrderStaffingPolicy.validate_can_assign_from_interest(
            order=locked_order,
            interest=locked_interest,
            has_current_assignment=current_assignment is not None,
        )

        locked_interest.status = ORDER_INTEREST_STATUS_ACCEPTED
        locked_interest.reviewed_by = assigned_by
        locked_interest.reviewed_at = timezone.now()
        locked_interest.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "updated_at",
            ]
        )

        assignment = OrderStaffingStore.create_assignment(
            order=locked_order,
            writer=locked_interest.writer,
            assigned_by=assigned_by,
            source=ORDER_ASSIGNMENT_SOURCE_ACCEPTED_INTEREST,
            source_interest=locked_interest,
        )

        OrderStaffingStore.close_other_open_interests(
            order=locked_order,
            keep_interest=locked_interest,
            superseded_status=ORDER_INTEREST_STATUS_SUPERSEDED,
        )
        cls._mark_order_in_progress(
            order=locked_order,
            actor=assigned_by,
            metadata={
                "assignment_id": assignment.pk,
                "interest_id": locked_interest.pk,
                "writer_id": getattr(locked_interest.writer, "pk", None),
                "source": ORDER_ASSIGNMENT_SOURCE_ACCEPTED_INTEREST,
            },
        )
        return assignment

    @classmethod
    @transaction.atomic
    def assign_directly(
        cls,
        *,
        order: Order,
        writer: Any,
        assigned_by: Any,
    ) -> OrderAssignment:
        locked_order = OrderStaffingStore.lock_order(order)
        current_assignment = OrderStaffingStore.get_current_assignment(
            order=locked_order
        )

        OrderStaffingPolicy.validate_can_assign_directly(
            order=locked_order,
            writer=writer,
            has_current_assignment=current_assignment is not None,
        )

        assignment = OrderStaffingStore.create_assignment(
            order=locked_order,
            writer=writer,
            assigned_by=assigned_by,
            source=ORDER_ASSIGNMENT_SOURCE_STAFF_ASSIGNMENT,
            source_interest=None,
        )

        OrderStaffingStore.close_other_open_interests(
            order=locked_order,
            superseded_status=ORDER_INTEREST_STATUS_SUPERSEDED,
        )
        cls._mark_order_in_progress(
            order=locked_order,
            actor=assigned_by,
            metadata={
                "assignment_id": assignment.pk,
                "writer_id": getattr(writer, "pk", None),
                "source": ORDER_ASSIGNMENT_SOURCE_STAFF_ASSIGNMENT,
            },
        )
        return assignment

    @classmethod
    @transaction.atomic
    def accept_preferred_writer_invitation(
        cls,
        *,
        interest: OrderInterest,
        writer: Any,
        triggered_by: Optional[Any] = None,
    ) -> OrderAssignment:
        locked_interest = OrderStaffingStore.lock_interest(interest)
        locked_order = OrderStaffingStore.lock_order(locked_interest.order)
        current_assignment = OrderStaffingStore.get_current_assignment(
            order=locked_order
        )

        OrderStaffingPolicy.validate_can_accept_preferred_invitation(
            order=locked_order,
            interest=locked_interest,
            writer=writer,
            has_current_assignment=current_assignment is not None,
        )

        locked_interest.status = ORDER_INTEREST_STATUS_ACCEPTED
        locked_interest.reviewed_by = triggered_by or writer
        locked_interest.reviewed_at = timezone.now()
        locked_interest.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "updated_at",
            ]
        )

        assignment = OrderStaffingStore.create_assignment(
            order=locked_order,
            writer=writer,
            assigned_by=triggered_by or writer,
            source=ORDER_ASSIGNMENT_SOURCE_PREFERRED_WRITER_ACCEPTANCE,
            source_interest=locked_interest,
        )

        OrderStaffingStore.close_other_open_interests(
            order=locked_order,
            keep_interest=locked_interest,
            superseded_status=ORDER_INTEREST_STATUS_SUPERSEDED,
        )
        cls._mark_order_in_progress(
            order=locked_order,
            actor=triggered_by or writer,
            metadata={
                "assignment_id": assignment.pk,
                "interest_id": locked_interest.pk,
                "writer_id": getattr(writer, "pk", None),
                "source": (
                    ORDER_ASSIGNMENT_SOURCE_PREFERRED_WRITER_ACCEPTANCE
                ),
            },
        )
        return assignment

    @classmethod
    @transaction.atomic
    def decline_preferred_writer_invitation(
        cls,
        *,
        interest: OrderInterest,
        writer: Any,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        locked_interest = OrderStaffingStore.lock_interest(interest)
        locked_order = OrderStaffingStore.lock_order(locked_interest.order)

        OrderStaffingPolicy.validate_can_decline_preferred_invitation(
            interest=locked_interest,
            writer=writer,
        )

        locked_interest.status = ORDER_INTEREST_STATUS_DECLINED
        locked_interest.reviewed_by = triggered_by or writer
        locked_interest.reviewed_at = timezone.now()
        locked_interest.withdrawn_at = timezone.now()
        locked_interest.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "withdrawn_at",
                "updated_at",
            ]
        )

        locked_order.preferred_writer_status = (
            PREFERRED_WRITER_STATUS_DECLINED
        )
        locked_order.visibility_mode = ORDER_VISIBILITY_POOL
        locked_order.save(
            update_fields=[
                "preferred_writer_status",
                "visibility_mode",
                "updated_at",
            ]
        )

        OrderStaffingEvents.preferred_writer_declined(
            order=locked_order,
            actor=triggered_by or writer,
            metadata={
                "interest_id": locked_interest.pk,
                "writer_id": getattr(writer, "pk", None),
            },
        )
        OrderStaffingEvents.pool_opened(
            order=locked_order,
            actor=triggered_by or writer,
            metadata={"source": "preferred_writer_decline"},
        )
        return locked_order

    @classmethod
    @transaction.atomic
    def expire_preferred_writer_invitation(
        cls,
        *,
        interest: OrderInterest,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        locked_interest = OrderStaffingStore.lock_interest(interest)
        locked_order = OrderStaffingStore.lock_order(locked_interest.order)

        OrderStaffingPolicy.validate_can_expire_preferred_invitation(
            interest=locked_interest,
        )

        locked_interest.status = ORDER_INTEREST_STATUS_EXPIRED
        locked_interest.reviewed_by = triggered_by
        locked_interest.reviewed_at = timezone.now()
        locked_interest.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "updated_at",
            ]
        )

        locked_order.preferred_writer_status = (
            PREFERRED_WRITER_STATUS_EXPIRED
        )
        locked_order.visibility_mode = ORDER_VISIBILITY_POOL
        locked_order.save(
            update_fields=[
                "preferred_writer_status",
                "visibility_mode",
                "updated_at",
            ]
        )

        OrderStaffingEvents.preferred_writer_expired(
            order=locked_order,
            actor=triggered_by,
            metadata={
                "interest_id": locked_interest.pk,
                "writer_id": getattr(locked_interest.writer, "pk", None),
            },
        )
        OrderStaffingEvents.pool_opened(
            order=locked_order,
            actor=triggered_by,
            metadata={"source": "preferred_writer_expiry"},
        )
        return locked_order

    @classmethod
    @transaction.atomic
    def release_to_pool(
        cls,
        *,
        order: Order,
        released_by: Optional[Any],
        reason: str,
    ) -> Order:
        locked_order = OrderStaffingStore.lock_order(order)
        current_assignment = OrderStaffingStore.get_current_assignment(
            order=locked_order
        )

        OrderStaffingPolicy.validate_can_release_to_pool(
            has_current_assignment=current_assignment is not None,
        )

        assert current_assignment is not None

        current_assignment.status = ORDER_ASSIGNMENT_STATUS_RELEASED
        current_assignment.is_current = False
        current_assignment.released_at = timezone.now()
        current_assignment.release_reason = reason
        current_assignment.save(
            update_fields=[
                "status",
                "is_current",
                "released_at",
                "release_reason",
                "updated_at",
            ]
        )

        locked_order.status = ORDER_STATUS_READY_FOR_STAFFING
        locked_order.visibility_mode = ORDER_VISIBILITY_POOL
        if locked_order.preferred_writer is None:
            locked_order.preferred_writer_status = (
                PREFERRED_WRITER_STATUS_NOT_REQUESTED
            )
        else:
            locked_order.preferred_writer_status = (
                PREFERRED_WRITER_STATUS_FALLBACK_TO_POOL
            )
        locked_order.save(
            update_fields=[
                "status",
                "visibility_mode",
                "preferred_writer_status",
                "updated_at",
            ]
        )

        OrderStaffingEvents.reassigned(
            order=locked_order,
            actor=released_by,
            metadata={
                "released_assignment_id": current_assignment.pk,
                "released_writer_id": getattr(
                    current_assignment.writer,
                    "pk",
                    None,
                ),
                "reason": reason,
                "action": "return_to_pool",
            },
        )
        OrderStaffingEvents.returned_to_pool(
            order=locked_order,
            actor=released_by,
            metadata={"reason": reason},
        )
        return locked_order

    @classmethod
    def _invite_preferred_writer(
        cls,
        *,
        order: Order,
        triggered_by: Optional[Any],
    ) -> Order:
        preferred_writer = order.preferred_writer
        if preferred_writer is None:
            raise ValueError(
                "Preferred writer invitation requires order.preferred_writer."
            )
        OrderStaffingPolicy.validate_writer_website(
            writer=preferred_writer,
            order=order,
        )

        has_open_invitation = OrderStaffingStore.has_open_invitation_of_type(
            order=order,
            interest_type=ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION,
        )
        OrderStaffingPolicy.validate_no_open_preferred_invitation(
            has_open_invitation=has_open_invitation,
        )

        interest = OrderInterest.objects.create(
            website=order.website,
            order=order,
            writer=preferred_writer,
            interest_type=ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION,
            status=ORDER_INTEREST_STATUS_PENDING,
            reviewed_by=triggered_by,
            reviewed_at=timezone.now() if triggered_by else None,
        )

        order.visibility_mode = ORDER_VISIBILITY_PREFERRED_WRITER_ONLY
        order.preferred_writer_status = PREFERRED_WRITER_STATUS_INVITED
        order.save(
            update_fields=[
                "visibility_mode",
                "preferred_writer_status",
                "updated_at",
            ]
        )

        OrderStaffingEvents.preferred_writer_invited(
            order=order,
            actor=triggered_by,
            metadata={
                "interest_id": interest.pk,
                "preferred_writer_id": getattr(preferred_writer, "pk", None),
            },
        )
        return order

    @classmethod
    def _open_order_to_pool(
        cls,
        *,
        order: Order,
        triggered_by: Optional[Any],
    ) -> Order:
        order.visibility_mode = ORDER_VISIBILITY_POOL
        if order.preferred_writer is None:
            order.preferred_writer_status = (
                PREFERRED_WRITER_STATUS_NOT_REQUESTED
            )
        order.save(
            update_fields=[
                "visibility_mode",
                "preferred_writer_status",
                "updated_at",
            ]
        )

        OrderStaffingEvents.pool_opened(
            order=order,
            actor=triggered_by,
            metadata={},
        )
        return order

    @classmethod
    def _mark_order_in_progress(
        cls,
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict,
    ) -> None:
        order.status = ORDER_STATUS_IN_PROGRESS
        order.visibility_mode = ORDER_VISIBILITY_HIDDEN
        if order.preferred_writer_status == PREFERRED_WRITER_STATUS_INVITED:
            order.preferred_writer_status = (
                PREFERRED_WRITER_STATUS_ACCEPTED
            )
        order.save(
            update_fields=[
                "status",
                "visibility_mode",
                "preferred_writer_status",
                "updated_at",
            ]
        )

        OrderStaffingEvents.assigned(
            order=order,
            actor=actor,
            metadata=metadata,
        )