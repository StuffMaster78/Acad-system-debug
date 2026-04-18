from __future__ import annotations

from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models import (
    Order,
    OrderAssignment,
    OrderInterest,
    OrderTimelineEvent,
)
from orders.models.orders.constants import (
    ORDER_ASSIGNMENT_SOURCE_ACCEPTED_INTEREST,
    ORDER_ASSIGNMENT_SOURCE_PREFERRED_WRITER_ACCEPTANCE,
    ORDER_ASSIGNMENT_SOURCE_SELF_TAKE,
    ORDER_ASSIGNMENT_SOURCE_STAFF_ASSIGNMENT,
    ORDER_ASSIGNMENT_STATUS_ACTIVE,
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
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_TIMELINE_EVENT_ASSIGNED,
    ORDER_TIMELINE_EVENT_INTEREST_CREATED,
    ORDER_TIMELINE_EVENT_POOL_OPENED,
    ORDER_TIMELINE_EVENT_PREFERRED_WRITER_DECLINED,
    ORDER_TIMELINE_EVENT_PREFERRED_WRITER_EXPIRED,
    ORDER_TIMELINE_EVENT_PREFERRED_WRITER_INVITED,
    ORDER_TIMELINE_EVENT_RETURNED_TO_POOL,
    ORDER_TIMELINE_EVENT_REASSIGNED,
    ORDER_TIMELINE_EVENT_INTEREST_WITHDRAWN,
    ORDER_VISIBILITY_HIDDEN,
    ORDER_VISIBILITY_POOL,
    ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
    PREFERRED_WRITER_STATUS_ACCEPTED,
    PREFERRED_WRITER_STATUS_DECLINED,
    PREFERRED_WRITER_STATUS_EXPIRED,
    PREFERRED_WRITER_STATUS_FALLBACK_TO_POOL,
    PREFERRED_WRITER_STATUS_INVITED,
    PREFERRED_WRITER_STATUS_NOT_REQUESTED,
)


class OrderStaffingService:
    """
    Own staffing visibility and assignment workflow for orders.

    This service handles:
        1. Preferred writer invitation flow
        2. Pool visibility flow
        3. Writer interest creation and withdrawal
        4. Writer self take flow
        5. Staff assignment flow
        6. Returning orders back to the pool

    This service does not handle:
        1. Reassignment request review
        2. Hold and resume
        3. Submission and completion
        4. Disputes
        5. Pricing and payment orchestration
    """

    @classmethod
    @transaction.atomic
    def route_order_to_staffing(
        cls,
        *,
        order: Order,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Route a staffing ready order into preferred writer or pool flow.

        Args:
            order:
                Staffing ready order.
            triggered_by:
                Optional actor initiating the routing.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the order is not staffing ready.
        """
        locked_order = cls._lock_order(order)

        cls._ensure_status(
            locked_order,
            allowed_statuses={ORDER_STATUS_READY_FOR_STAFFING},
            message="Only staffing ready orders can be routed.",
        )
        cls._ensure_no_current_assignment(locked_order)

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
        """
        Create a writer interest record for a pool visible order.

        Args:
            order:
                Order the writer wants to work on.
            writer:
                Writer expressing interest.
            message:
                Optional message from the writer.
            triggered_by:
                Optional actor performing the action.

        Returns:
            OrderInterest:
                Created interest record.

        Raises:
            ValidationError:
                Raised when the order is not eligible for interest.
        """
        locked_order = cls._lock_order(order)

        cls._ensure_status(
            locked_order,
            allowed_statuses={ORDER_STATUS_READY_FOR_STAFFING},
            message="Only staffing ready orders can accept interest.",
        )
        cls._ensure_visibility_mode(
            locked_order,
            allowed_modes={ORDER_VISIBILITY_POOL},
            message="Only pool visible orders accept general interest.",
        )
        cls._ensure_no_current_assignment(locked_order)

        cls._validate_writer_website(writer=writer, order=locked_order)

        existing_interest = (
            OrderInterest.objects.select_for_update()
            .filter(
                order=locked_order,
                writer=writer,
                status=ORDER_INTEREST_STATUS_PENDING,
            )
            .first()
        )
        if existing_interest is not None:
            raise ValidationError(
                "Writer already has a pending interest for this order."
            )

        interest = OrderInterest.objects.create(
            website=locked_order.website,
            order=locked_order,
            writer=writer,
            interest_type=ORDER_INTEREST_TYPE_SHOW_INTEREST,
            status=ORDER_INTEREST_STATUS_PENDING,
            message=message,
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_INTEREST_CREATED,
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
        """
        Withdraw a pending writer interest record.

        Args:
            interest:
                Interest record to withdraw.
            writer:
                Writer withdrawing the interest.
            triggered_by:
                Optional actor performing the action.

        Returns:
            OrderInterest:
                Updated interest record.

        Raises:
            ValidationError:
                Raised when the interest cannot be withdrawn.
        """
        locked_interest = cls._lock_interest(interest)

        if locked_interest.writer != writer:
            raise ValidationError(
                "Only the writer who created the interest can withdraw it."
            )

        if locked_interest.status != ORDER_INTEREST_STATUS_PENDING:
            raise ValidationError(
                "Only pending interest can be withdrawn."
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

        cls._create_timeline_event(
            order=locked_interest.order,
            event_type=ORDER_TIMELINE_EVENT_INTEREST_WITHDRAWN,
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
        """
        Let an eligible writer self take a staffing ready order.

        Args:
            order:
                Staffing ready order.
            writer:
                Writer taking the order.
            triggered_by:
                Optional actor performing the action.

        Returns:
            OrderAssignment:
                Created assignment record.

        Raises:
            ValidationError:
                Raised when the order cannot be taken.
        """
        locked_order = cls._lock_order(order)

        cls._ensure_status(
            locked_order,
            allowed_statuses={ORDER_STATUS_READY_FOR_STAFFING},
            message="Only staffing ready orders can be taken.",
        )
        cls._ensure_visibility_mode(
            locked_order,
            allowed_modes={ORDER_VISIBILITY_POOL},
            message="Only pool visible orders can be taken.",
        )
        cls._ensure_no_current_assignment(locked_order)
        cls._validate_writer_website(writer=writer, order=locked_order)

        existing_interest = (
            OrderInterest.objects.select_for_update()
            .filter(
                order=locked_order,
                writer=writer,
                interest_type=ORDER_INTEREST_TYPE_REQUEST_TAKE,
                status=ORDER_INTEREST_STATUS_PENDING,
            )
            .first()
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

        assignment = cls._create_assignment(
            order=locked_order,
            writer=writer,
            assigned_by=triggered_by or writer,
            source=ORDER_ASSIGNMENT_SOURCE_SELF_TAKE,
            source_interest=existing_interest,
        )

        cls._close_other_open_interests(
            order=locked_order,
            keep_interest=existing_interest,
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
        """
        Assign an order to a writer from an existing interest record.

        Args:
            interest:
                Winning interest record.
            assigned_by:
                Staff actor creating the assignment.

        Returns:
            OrderAssignment:
                Created assignment record.

        Raises:
            ValidationError:
                Raised when the order cannot be assigned.
        """
        locked_interest = cls._lock_interest(interest)
        locked_order = cls._lock_order(locked_interest.order)

        cls._ensure_status(
            locked_order,
            allowed_statuses={ORDER_STATUS_READY_FOR_STAFFING},
            message="Only staffing ready orders can be assigned.",
        )
        cls._ensure_no_current_assignment(locked_order)

        if locked_interest.status != ORDER_INTEREST_STATUS_PENDING:
            raise ValidationError(
                "Only pending interest can be assigned."
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

        assignment = cls._create_assignment(
            order=locked_order,
            writer=locked_interest.writer,
            assigned_by=assigned_by,
            source=ORDER_ASSIGNMENT_SOURCE_ACCEPTED_INTEREST,
            source_interest=locked_interest,
        )

        cls._close_other_open_interests(
            order=locked_order,
            keep_interest=locked_interest,
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
        """
        Assign an order directly to a writer without accepting interest.

        Args:
            order:
                Staffing ready order.
            writer:
                Writer receiving the assignment.
            assigned_by:
                Staff actor assigning the order.

        Returns:
            OrderAssignment:
                Created assignment record.

        Raises:
            ValidationError:
                Raised when the order cannot be assigned.
        """
        locked_order = cls._lock_order(order)

        cls._ensure_status(
            locked_order,
            allowed_statuses={ORDER_STATUS_READY_FOR_STAFFING},
            message="Only staffing ready orders can be assigned.",
        )
        cls._ensure_no_current_assignment(locked_order)
        cls._validate_writer_website(writer=writer, order=locked_order)

        assignment = cls._create_assignment(
            order=locked_order,
            writer=writer,
            assigned_by=assigned_by,
            source=ORDER_ASSIGNMENT_SOURCE_STAFF_ASSIGNMENT,
            source_interest=None,
        )

        cls._close_other_open_interests(order=locked_order)
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
        """
        Accept a pending preferred writer invitation and assign the order.

        Args:
            interest:
                Preferred writer invitation interest.
            writer:
                Invited preferred writer.
            triggered_by:
                Optional actor performing the action.

        Returns:
            OrderAssignment:
                Created assignment record.

        Raises:
            ValidationError:
                Raised when the invitation cannot be accepted.
        """
        locked_interest = cls._lock_interest(interest)
        locked_order = cls._lock_order(locked_interest.order)

        cls._ensure_status(
            locked_order,
            allowed_statuses={ORDER_STATUS_READY_FOR_STAFFING},
            message="Only staffing ready orders can be assigned.",
        )
        cls._ensure_no_current_assignment(locked_order)
        cls._validate_writer_website(writer=writer, order=locked_order)

        if locked_interest.writer != writer:
            raise ValidationError(
                "Only the invited writer can accept this invitation."
            )

        if (
            locked_interest.interest_type
            != ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION
        ):
            raise ValidationError(
                "Interest is not a preferred writer invitation."
            )

        if locked_interest.status != ORDER_INTEREST_STATUS_PENDING:
            raise ValidationError(
                "Only pending preferred writer invitations can be accepted."
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

        assignment = cls._create_assignment(
            order=locked_order,
            writer=writer,
            assigned_by=triggered_by or writer,
            source=ORDER_ASSIGNMENT_SOURCE_PREFERRED_WRITER_ACCEPTANCE,
            source_interest=locked_interest,
        )

        cls._close_other_open_interests(
            order=locked_order,
            keep_interest=locked_interest,
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
        """
        Decline a pending preferred writer invitation and open the pool.

        Args:
            interest:
                Preferred writer invitation interest.
            writer:
                Invited preferred writer.
            triggered_by:
                Optional actor performing the action.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the invitation cannot be declined.
        """
        locked_interest = cls._lock_interest(interest)
        locked_order = cls._lock_order(locked_interest.order)

        if locked_interest.writer != writer:
            raise ValidationError(
                "Only the invited writer can decline this invitation."
            )

        if (
            locked_interest.interest_type
            != ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION
        ):
            raise ValidationError(
                "Interest is not a preferred writer invitation."
            )

        if locked_interest.status != ORDER_INTEREST_STATUS_PENDING:
            raise ValidationError(
                "Only pending preferred writer invitations can be declined."
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

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_PREFERRED_WRITER_DECLINED,
            actor=triggered_by or writer,
            metadata={
                "interest_id": locked_interest.pk,
                "writer_id": getattr(writer, "pk", None),
            },
        )
        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_POOL_OPENED,
            actor=triggered_by or writer,
            metadata={
                "source": "preferred_writer_decline",
            },
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
        """
        Expire a pending preferred writer invitation and open the pool.

        Args:
            interest:
                Preferred writer invitation interest.
            triggered_by:
                Optional actor performing the action.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the invitation cannot be expired.
        """
        locked_interest = cls._lock_interest(interest)
        locked_order = cls._lock_order(locked_interest.order)

        if (
            locked_interest.interest_type
            != ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION
        ):
            raise ValidationError(
                "Interest is not a preferred writer invitation."
            )

        if locked_interest.status != ORDER_INTEREST_STATUS_PENDING:
            raise ValidationError(
                "Only pending preferred writer invitations can expire."
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

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_PREFERRED_WRITER_EXPIRED,
            actor=triggered_by,
            metadata={
                "interest_id": locked_interest.pk,
                "writer_id": getattr(locked_interest.writer, "pk", None),
            },
        )
        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_POOL_OPENED,
            actor=triggered_by,
            metadata={
                "source": "preferred_writer_expiry",
            },
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
        """
        Return an actively assigned order back to the staffing pool.

        Args:
            order:
                Order being returned to the pool.
            released_by:
                Optional actor releasing the order.
            reason:
                Reason for releasing the order.

        Returns:
            Order:
                Updated order.

        Raises:
            ValidationError:
                Raised when the order cannot be returned to pool.
        """
        locked_order = cls._lock_order(order)
        current_assignment = cls._get_current_assignment(locked_order)

        if current_assignment is None:
            raise ValidationError(
                "Cannot return an order to the pool without an assignment."
            )

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

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_REASSIGNED,
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
        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_RETURNED_TO_POOL,
            actor=released_by,
            metadata={
                "reason": reason,
            },
        )
        return locked_order

    @classmethod
    def _invite_preferred_writer(
        cls,
        *,
        order: Order,
        triggered_by: Optional[Any],
    ) -> Order:
        """
        Put the order into preferred writer only visibility mode.

        Args:
            order:
                Staffing ready order.
            triggered_by:
                Optional actor initiating the routing.

        Returns:
            Order:
                Updated order.
        """
        preferred_writer = order.preferred_writer
        if preferred_writer is None:
            raise ValidationError(
                "Preferred writer invitation requires a preferred writer."
            )

        cls._validate_writer_website(
            writer=preferred_writer,
            order=order,
        )
        cls._ensure_no_open_preferred_invitation(order)

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

        cls._create_timeline_event(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_PREFERRED_WRITER_INVITED,
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
        """
        Make a staffing ready order visible to the general pool.

        Args:
            order:
                Staffing ready order.
            triggered_by:
                Optional actor initiating the visibility change.

        Returns:
            Order:
                Updated order.
        """
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

        cls._create_timeline_event(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_POOL_OPENED,
            actor=triggered_by,
            metadata={},
        )
        return order

    @classmethod
    def _create_assignment(
        cls,
        *,
        order: Order,
        writer: Any,
        assigned_by: Optional[Any],
        source: str,
        source_interest: Optional[OrderInterest],
    ) -> OrderAssignment:
        """
        Create a new active assignment for an order.

        Args:
            order:
                Order receiving the assignment.
            writer:
                Writer being assigned.
            assigned_by:
                Optional actor creating the assignment.
            source:
                Assignment source enum value.
            source_interest:
                Optional interest that produced the assignment.

        Returns:
            OrderAssignment:
                Created assignment record.
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

    @classmethod
    def _close_other_open_interests(
        cls,
        *,
        order: Order,
        keep_interest: Optional[OrderInterest] = None,
    ) -> None:
        """
        Close competing open interest records after assignment.

        Args:
            order:
                Order whose open interests should be closed.
            keep_interest:
                Interest to keep untouched, if any.
        """
        queryset = OrderInterest.objects.select_for_update().filter(
            order=order,
            status=ORDER_INTEREST_STATUS_PENDING,
        )

        if keep_interest is not None:
            queryset = queryset.exclude(pk=keep_interest.pk)

        queryset.update(
            status=ORDER_INTEREST_STATUS_SUPERSEDED,
            reviewed_at=timezone.now(),
        )

    @classmethod
    def _mark_order_in_progress(
        cls,
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict,
    ) -> None:
        """
        Move an order from staffing ready to in progress.

        Args:
            order:
                Order being activated.
            actor:
                Optional actor causing the transition.
            metadata:
                Structured metadata for the timeline event.
        """
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

        cls._create_timeline_event(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_ASSIGNED,
            actor=actor,
            metadata=metadata,
        )

    @classmethod
    def _ensure_status(
        cls,
        order: Order,
        *,
        allowed_statuses: set[str],
        message: str,
    ) -> None:
        """
        Ensure the order is in one of the allowed statuses.

        Args:
            order:
                Order being validated.
            allowed_statuses:
                Allowed lifecycle states.
            message:
                Error message when validation fails.

        Raises:
            ValidationError:
                Raised when the order status is not allowed.
        """
        if order.status not in allowed_statuses:
            raise ValidationError(message)

    @classmethod
    def _ensure_visibility_mode(
        cls,
        order: Order,
        *,
        allowed_modes: set[str],
        message: str,
    ) -> None:
        """
        Ensure the order visibility mode is allowed.

        Args:
            order:
                Order being validated.
            allowed_modes:
                Allowed visibility modes.
            message:
                Error message when validation fails.

        Raises:
            ValidationError:
                Raised when the order visibility mode is not allowed.
        """
        if order.visibility_mode not in allowed_modes:
            raise ValidationError(message)

    @classmethod
    def _ensure_no_current_assignment(cls, order: Order) -> None:
        """
        Ensure an order does not already have an active assignment.

        Args:
            order:
                Order being validated.

        Raises:
            ValidationError:
                Raised when an active assignment already exists.
        """
        current_assignment = cls._get_current_assignment(order)
        if current_assignment is not None:
            raise ValidationError(
                "Order already has an active assignment."
            )

    @classmethod
    def _ensure_no_open_preferred_invitation(cls, order: Order) -> None:
        """
        Ensure the order does not already have an open preferred invite.

        Args:
            order:
                Order being validated.

        Raises:
            ValidationError:
                Raised when an open preferred writer invitation exists.
        """
        open_invitation_exists = (
            OrderInterest.objects.select_for_update()
            .filter(
                order=order,
                interest_type=(
                    ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION
                ),
                status=ORDER_INTEREST_STATUS_PENDING,
            )
            .exists()
        )

        if open_invitation_exists:
            raise ValidationError(
                "Order already has an open preferred writer invitation."
            )

    @classmethod
    def _validate_writer_website(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> None:
        """
        Ensure the writer belongs to the same tenant as the order.

        Args:
            writer:
                Writer being validated.
            order:
                Order being validated.

        Raises:
            ValidationError:
                Raised when the writer crosses tenants.
        """
        writer_website_id = getattr(writer, "website_id", None)
        if (
            writer_website_id is not None
            and writer_website_id != order.website.pk
        ):
            raise ValidationError(
                "Writer website must match order website."
            )

    @classmethod
    def _get_current_assignment(
        cls,
        order: Order,
    ) -> Optional[OrderAssignment]:
        """
        Return the current active assignment for an order.

        Args:
            order:
                Order whose assignment is needed.

        Returns:
            Optional[OrderAssignment]:
                Current active assignment, if any.
        """
        return (
            OrderAssignment.objects.select_for_update()
            .filter(
                order=order,
                is_current=True,
            )
            .select_related("writer")
            .first()
        )

    @classmethod
    def _lock_order(cls, order: Order) -> Order:
        """
        Lock and reload an order inside a transaction.

        Args:
            order:
                Order to lock.

        Returns:
            Order:
                Locked order instance.
        """
        return Order.objects.select_for_update().get(pk=order.pk)

    @classmethod
    def _lock_interest(cls, interest: OrderInterest) -> OrderInterest:
        """
        Lock and reload an interest inside a transaction.

        Args:
            interest:
                Interest to lock.

        Returns:
            OrderInterest:
                Locked interest instance.
        """
        return OrderInterest.objects.select_for_update().get(pk=interest.pk)

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
        Create a timeline event for staffing workflow changes.

        Args:
            order:
                Order receiving the event.
            event_type:
                Event type enum value.
            actor:
                Optional actor associated with the event.
            metadata:
                Structured event payload.

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