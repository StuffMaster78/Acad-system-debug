from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction

from orders.models.adjustments.order_adjustment_event import (
    OrderAdjustmentEvent,
)
from orders.models.adjustments.order_adjustment_proposal import (
    OrderAdjustmentProposal,
)
from orders.models.adjustments.order_adjustment_request import (
    OrderAdjustmentRequest,
)
from orders.models.orders.order import Order
from orders.models.orders.constants import (
    ORDER_ADJUSTMENT_EVENT_ACCEPTED,
    ORDER_ADJUSTMENT_EVENT_CANCELLED,
    ORDER_ADJUSTMENT_EVENT_CLIENT_COUNTERED,
    ORDER_ADJUSTMENT_EVENT_DECLINED,
    ORDER_ADJUSTMENT_EVENT_EXPIRED,
    ORDER_ADJUSTMENT_EVENT_PROPOSAL_CREATED,
    ORDER_ADJUSTMENT_EVENT_REQUEST_CREATED,
    ORDER_ADJUSTMENT_PROPOSAL_ROLE_CLIENT,
    ORDER_ADJUSTMENT_PROPOSAL_ROLE_STAFF,
    ORDER_ADJUSTMENT_PROPOSAL_ROLE_SYSTEM,
    ORDER_ADJUSTMENT_PROPOSAL_ROLE_WRITER,
    ORDER_ADJUSTMENT_PROPOSAL_TYPE_CLIENT_COUNTER,
    ORDER_ADJUSTMENT_PROPOSAL_TYPE_FINAL_AGREEMENT,
    ORDER_ADJUSTMENT_PROPOSAL_TYPE_STAFF_OVERRIDE,
    ORDER_ADJUSTMENT_PROPOSAL_TYPE_SYSTEM_QUOTE,
    ORDER_ADJUSTMENT_STATUS_ACCEPTED,
    ORDER_ADJUSTMENT_STATUS_CANCELLED,
    ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED,
    ORDER_ADJUSTMENT_STATUS_DECLINED,
    ORDER_ADJUSTMENT_STATUS_EXPIRED,
    ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
)


class AdjustmentNegotiationService:
    """
    Own negotiation workflow for commercial order adjustments.
    """

    @classmethod
    @transaction.atomic
    def create_request_with_system_quote(
        cls,
        *,
        order: Order,
        requested_by: Any,
        adjustment_type: str,
        reason: str,
        quoted_amount: Decimal,
        scope_summary: str,
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentRequest:
        """
        Create an adjustment request and its initial system quote.
        """
        locked_order = cls._lock_order(order)

        cls._validate_actor_website(actor=requested_by, order=locked_order)
        cls._validate_amount(quoted_amount)

        adjustment_request = OrderAdjustmentRequest.objects.create(
            website=locked_order.website,
            order=locked_order,
            requested_by=requested_by,
            adjustment_type=adjustment_type,
            reason=reason,
            status=ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
            metadata={
                "scope_summary": scope_summary,
                "requested_by_id": getattr(requested_by, "pk", None),
            },
        )

        cls._create_event(
            adjustment_request=adjustment_request,
            event_type=ORDER_ADJUSTMENT_EVENT_REQUEST_CREATED,
            actor=triggered_by or requested_by,
            metadata={
                "adjustment_type": adjustment_type,
                "reason": reason,
            },
        )

        cls._create_proposal(
            adjustment_request=adjustment_request,
            proposal_type=ORDER_ADJUSTMENT_PROPOSAL_TYPE_SYSTEM_QUOTE,
            proposed_by_role=ORDER_ADJUSTMENT_PROPOSAL_ROLE_SYSTEM,
            amount=quoted_amount,
            notes="Initial system quote",
            actor=triggered_by or requested_by,
            metadata={
                "scope_summary": scope_summary,
            },
        )

        return adjustment_request

    @classmethod
    @transaction.atomic
    def create_staff_override_proposal(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        proposed_by: Any,
        amount: Decimal,
        notes: str,
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentProposal:
        """
        Create a staff override proposal on an open adjustment request.
        """
        locked_request = cls._lock_request(adjustment_request)

        cls._ensure_request_open_for_negotiation(locked_request)
        cls._validate_actor_website(
            actor=proposed_by,
            order=locked_request.order,
        )
        cls._validate_amount(amount)

        proposal = cls._create_proposal(
            adjustment_request=locked_request,
            proposal_type=ORDER_ADJUSTMENT_PROPOSAL_TYPE_STAFF_OVERRIDE,
            proposed_by_role=ORDER_ADJUSTMENT_PROPOSAL_ROLE_STAFF,
            amount=amount,
            notes=notes,
            actor=triggered_by or proposed_by,
            metadata={},
        )

        locked_request.status = ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE
        locked_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
        return proposal

    @classmethod
    @transaction.atomic
    def counter_by_client(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        client: Any,
        amount: Decimal,
        notes: str,
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentProposal:
        """
        Record a client counter proposal.
        """
        locked_request = cls._lock_request(adjustment_request)

        cls._ensure_request_open_for_negotiation(locked_request)
        cls._validate_actor_website(actor=client, order=locked_request.order)
        cls._validate_amount(amount)

        proposal = cls._create_proposal(
            adjustment_request=locked_request,
            proposal_type=ORDER_ADJUSTMENT_PROPOSAL_TYPE_CLIENT_COUNTER,
            proposed_by_role=ORDER_ADJUSTMENT_PROPOSAL_ROLE_CLIENT,
            amount=amount,
            notes=notes,
            actor=triggered_by or client,
            metadata={},
        )

        locked_request.status = ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED
        locked_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        cls._create_event(
            adjustment_request=locked_request,
            event_type=ORDER_ADJUSTMENT_EVENT_CLIENT_COUNTERED,
            actor=triggered_by or client,
            metadata={
                "proposal_id": proposal.pk,
                "amount": str(amount),
            },
        )
        return proposal

    @classmethod
    @transaction.atomic
    def accept_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        accepted_by: Any,
        final_amount: Decimal,
        notes: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentProposal:
        """
        Accept an adjustment request and create the final agreement proposal.
        """
        locked_request = cls._lock_request(adjustment_request)

        cls._ensure_request_open_for_negotiation(locked_request)
        cls._validate_actor_website(
            actor=accepted_by,
            order=locked_request.order,
        )
        cls._validate_amount(final_amount)

        final_proposal = cls._create_proposal(
            adjustment_request=locked_request,
            proposal_type=ORDER_ADJUSTMENT_PROPOSAL_TYPE_FINAL_AGREEMENT,
            proposed_by_role=ORDER_ADJUSTMENT_PROPOSAL_ROLE_CLIENT,
            amount=final_amount,
            notes=notes or "Final agreement accepted",
            actor=triggered_by or accepted_by,
            metadata={},
        )

        locked_request.status = ORDER_ADJUSTMENT_STATUS_ACCEPTED
        locked_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        cls._create_event(
            adjustment_request=locked_request,
            event_type=ORDER_ADJUSTMENT_EVENT_ACCEPTED,
            actor=triggered_by or accepted_by,
            metadata={
                "proposal_id": final_proposal.pk,
                "final_amount": str(final_amount),
            },
        )
        return final_proposal

    @classmethod
    @transaction.atomic
    def decline_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        declined_by: Any,
        reason: str,
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentRequest:
        """
        Decline an open adjustment request.
        """
        locked_request = cls._lock_request(adjustment_request)

        cls._ensure_request_open_for_negotiation(locked_request)
        cls._validate_actor_website(
            actor=declined_by,
            order=locked_request.order,
        )

        locked_request.status = ORDER_ADJUSTMENT_STATUS_DECLINED
        locked_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        cls._create_event(
            adjustment_request=locked_request,
            event_type=ORDER_ADJUSTMENT_EVENT_DECLINED,
            actor=triggered_by or declined_by,
            metadata={
                "reason": reason,
            },
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def cancel_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        cancelled_by: Any,
        reason: str,
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentRequest:
        """
        Cancel an open adjustment request.
        """
        locked_request = cls._lock_request(adjustment_request)

        cls._ensure_request_open_for_negotiation(locked_request)
        cls._validate_actor_website(
            actor=cancelled_by,
            order=locked_request.order,
        )

        locked_request.status = ORDER_ADJUSTMENT_STATUS_CANCELLED
        locked_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        cls._create_event(
            adjustment_request=locked_request,
            event_type=ORDER_ADJUSTMENT_EVENT_CANCELLED,
            actor=triggered_by or cancelled_by,
            metadata={
                "reason": reason,
            },
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def expire_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentRequest:
        """
        Expire an open adjustment request.
        """
        locked_request = cls._lock_request(adjustment_request)

        cls._ensure_request_open_for_negotiation(locked_request)

        locked_request.status = ORDER_ADJUSTMENT_STATUS_EXPIRED
        locked_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        cls._create_event(
            adjustment_request=locked_request,
            event_type=ORDER_ADJUSTMENT_EVENT_EXPIRED,
            actor=triggered_by,
            metadata={},
        )
        return locked_request

    @classmethod
    def _ensure_request_open_for_negotiation(
        cls,
        adjustment_request: OrderAdjustmentRequest,
    ) -> None:
        """
        Ensure adjustment request is still negotiable.
        """
        allowed_statuses = {
            ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
            ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED,
        }
        if adjustment_request.status not in allowed_statuses:
            raise ValidationError(
                "Only open adjustment requests can be negotiated."
            )

    @classmethod
    def _validate_amount(cls, amount: Decimal) -> None:
        """
        Ensure a proposal amount is valid.
        """
        if amount <= 0:
            raise ValidationError(
                "Adjustment amount must be greater than zero."
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
    def _lock_request(
        cls,
        adjustment_request: OrderAdjustmentRequest,
    ) -> OrderAdjustmentRequest:
        """
        Lock and reload an adjustment request inside a transaction.
        """
        return OrderAdjustmentRequest.objects.select_for_update().get(
            pk=adjustment_request.pk
        )

    @classmethod
    def _create_proposal(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        proposal_type: str,
        proposed_by_role: str,
        amount: Decimal,
        notes: str,
        actor: Optional[Any],
        metadata: dict,
    ) -> OrderAdjustmentProposal:
        """
        Create an adjustment proposal and its creation event.
        """
        proposal = OrderAdjustmentProposal.objects.create(
            website=adjustment_request.website,
            adjustment_request=adjustment_request,
            proposal_type=proposal_type,
            proposed_by_role=proposed_by_role,
            amount=amount,
            notes=notes,
            metadata=metadata,
        )

        cls._create_event(
            adjustment_request=adjustment_request,
            event_type=ORDER_ADJUSTMENT_EVENT_PROPOSAL_CREATED,
            actor=actor,
            metadata={
                "proposal_id": proposal.pk,
                "proposal_type": proposal_type,
                "proposed_by_role": proposed_by_role,
                "amount": str(amount),
            },
        )
        return proposal

    @classmethod
    def _create_event(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        event_type: str,
        actor: Optional[Any],
        metadata: dict,
    ) -> OrderAdjustmentEvent:
        """
        Create an adjustment event.
        """
        return OrderAdjustmentEvent.objects.create(
            website=adjustment_request.website,
            adjustment_request=adjustment_request,
            event_type=event_type,
            actor=actor,
            metadata=metadata,
        )