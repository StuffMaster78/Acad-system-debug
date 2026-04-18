from __future__ import annotations

from datetime import timedelta
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.revisions.order_revision_event import (
    OrderRevisionEvent,
)
from orders.models.revisions.order_revision_request import (
    OrderRevisionRequest,
)
from orders.models.adjustments.order_adjustment_request import (
    OrderAdjustmentRequest,
)
from orders.models.orders.order import Order
from orders.models.orders.constants import (
    FREE_REVISION_WINDOW_DAYS,
    ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
    ORDER_ADJUSTMENT_TYPE_PAID_REVISION,
    ORDER_REVISION_EVENT_CREATED,
    ORDER_REVISION_STATUS_PENDING,
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_SUBMITTED,
)


class RevisionOrchestrationService:
    """
    Decide whether a revision request is free or paid.

    This service owns:
        1. Free revision eligibility window
        2. Scope fit routing
        3. Free revision creation
        4. Paid revision adjustment routing

    This service does not own:
        1. Funding
        2. Adjustment negotiation
        3. Submission workflow
        4. Dispute workflow
    """

    @classmethod
    @transaction.atomic
    def create_revision_request(
        cls,
        *,
        order: Order,
        requested_by: Any,
        reason: str,
        scope_summary: str,
        is_within_original_scope: bool,
        triggered_by: Optional[Any] = None,
    ) -> OrderRevisionRequest | OrderAdjustmentRequest:
        """
        Route a revision request into free revision or paid revision.

        Args:
            order:
                Completed order being reviewed for revision.
            requested_by:
                Actor requesting the revision.
            reason:
                Reason for the revision request.
            scope_summary:
                Summary of the requested change.
            is_within_original_scope:
                Whether the requested change fits the original scope.
            triggered_by:
                Optional actor performing the action.

        Returns:
            OrderRevisionRequest | OrderAdjustmentRequest:
                Free revision request when eligible, otherwise a paid
                revision adjustment request.

        Raises:
            ValidationError:
                Raised when the order is not eligible for revision routing.
        """
        locked_order = cls._lock_order(order)

        cls._ensure_order_can_accept_revision(locked_order)
        cls._validate_actor_website(actor=requested_by, order=locked_order)

        if cls._is_free_revision_eligible(
            order=locked_order,
            is_within_original_scope=is_within_original_scope,
        ):
            return cls._create_free_revision_request(
                order=locked_order,
                requested_by=requested_by,
                reason=reason,
                scope_summary=scope_summary,
                triggered_by=triggered_by,
            )

        return cls._create_paid_revision_adjustment(
            order=locked_order,
            requested_by=requested_by,
            reason=reason,
            scope_summary=scope_summary,
            is_within_original_scope=is_within_original_scope,
            triggered_by=triggered_by,
        )

    @classmethod
    def _is_free_revision_eligible(
        cls,
        *,
        order: Order,
        is_within_original_scope: bool,
    ) -> bool:
        """
        Determine whether the revision qualifies as free.

        Free revision requires:
            1. Order completed_at exists
            2. Request falls within the configured window
            3. Request stays within original scope
        """
        reference_time = (
            order.completed_at
            or getattr(order, "submitted_at", None)
        )

        if reference_time is None:
            return False

        if not is_within_original_scope:
            return False

        revision_deadline = reference_time + timedelta(
            days=FREE_REVISION_WINDOW_DAYS
        )
        return timezone.now() <= revision_deadline

    @classmethod
    def _create_free_revision_request(
        cls,
        *,
        order: Order,
        requested_by: Any,
        reason: str,
        scope_summary: str,
        triggered_by: Optional[Any] = None,
    ) -> OrderRevisionRequest:
        """
        Create a free revision request and its creation event.
        """
        revision_request = OrderRevisionRequest.objects.create(
            website=order.website,
            order=order,
            requested_by=requested_by,
            reason=reason,
            scope_summary=scope_summary,
            status=ORDER_REVISION_STATUS_PENDING,
        )

        cls._create_revision_event(
            revision_request=revision_request,
            event_type=ORDER_REVISION_EVENT_CREATED,
            actor=triggered_by or requested_by,
            metadata={
                "requested_by_id": getattr(requested_by, "pk", None),
                "scope_summary": scope_summary,
                "routing": "free_revision",
            },
        )
        return revision_request

    @classmethod
    def _create_paid_revision_adjustment(
        cls,
        *,
        order: Order,
        requested_by: Any,
        reason: str,
        scope_summary: str,
        is_within_original_scope: bool,
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentRequest:
        """
        Route the revision request into a paid revision adjustment.
        """
        reject_reason = cls._build_paid_revision_reject_reason(
            order=order,
            is_within_original_scope=is_within_original_scope,
        )

        adjustment_request = OrderAdjustmentRequest.objects.create(
            website=order.website,
            order=order,
            requested_by=requested_by,
            adjustment_type=ORDER_ADJUSTMENT_TYPE_PAID_REVISION,
            reason=reason,
            status=ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
            metadata={
                "scope_summary": scope_summary,
                "revision_routing": "paid_revision",
                "reject_revision_reason": reject_reason,
                "requested_by_id": getattr(requested_by, "pk", None),
                "triggered_by_id": getattr(triggered_by, "pk", None),
            },
        )

        return adjustment_request

    @classmethod
    def _build_paid_revision_reject_reason(
        cls,
        *,
        order: Order,
        is_within_original_scope: bool,
    ) -> str:
        """
        Explain why the request is not eligible for free revision.
        """
        reference_time = (
            order.completed_at
            or getattr(order, "submitted_at", None)
        )
        if reference_time is None:
            return "revision_reference_time_missing"

        if not is_within_original_scope:
            return "out_of_scope"

        revision_deadline = reference_time + timedelta(
            days=FREE_REVISION_WINDOW_DAYS
        )
        if timezone.now() > revision_deadline:
            return "free_revision_window_expired"

        return "paid_revision_required"

    @classmethod
    def _ensure_order_can_accept_revision(cls, order: Order) -> None:
        """
        Ensure the order is in a state that can accept revision routing.
        """
        if order.status not in {
            ORDER_STATUS_SUBMITTED,
            ORDER_STATUS_COMPLETED,
        }:
            raise ValidationError(
                "Only submitted or completed orders can enter revision routing."
            )
        if getattr(order, "approved_at", None) is not None:
            raise ValidationError(
                "Approved orders cannot be revised unless overridden."
            )
        
        reference_time = (
            order.completed_at
            or getattr(order, "submitted_at", None)
        )
        if reference_time is None:
            raise ValidationError(
                "Submitted or completed orders must have a revision reference time."
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
    def _create_revision_event(
        cls,
        *,
        revision_request: OrderRevisionRequest,
        event_type: str,
        actor: Optional[Any],
        metadata: dict,
    ) -> OrderRevisionEvent:
        """
        Create a revision event.
        """
        return OrderRevisionEvent.objects.create(
            website=revision_request.website,
            revision_request=revision_request,
            event_type=event_type,
            actor=actor,
            metadata=metadata,
        )