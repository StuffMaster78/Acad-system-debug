from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.adjustments.order_adjustment_event import (
    OrderAdjustmentEvent,
)
from orders.models.adjustments.order_adjustment_funding import (
    OrderAdjustmentFunding,
)
from orders.models.adjustments.order_adjustment_request import (
    OrderAdjustmentRequest,
)
from orders.models.adjustments.order_compensation_adjustment import (
    OrderCompensationAdjustment,
)
from orders.services.adjustment_negotiation_service import (
    AdjustmentNegotiationService,
)
from orders.services.adjustment_scope_application_service import (
    AdjustmentScopeApplicationService,
)
from orders.models.orders.constants import (
    ORDER_ADJUSTMENT_EVENT_BILLING_CREATED,
    ORDER_ADJUSTMENT_EVENT_COMPENSATION_CREATED,
    ORDER_ADJUSTMENT_EVENT_FUNDED,
    ORDER_ADJUSTMENT_EVENT_PAYMENT_FULLY_APPLIED,
    ORDER_ADJUSTMENT_EVENT_PAYMENT_INTENT_CREATED,
    ORDER_ADJUSTMENT_EVENT_PAYMENT_PARTIALLY_APPLIED,
    ORDER_ADJUSTMENT_FUNDING_STATUS_FUNDED,
    ORDER_ADJUSTMENT_FUNDING_STATUS_NOT_STARTED,
    ORDER_ADJUSTMENT_FUNDING_STATUS_PARTIALLY_FUNDED,
    ORDER_ADJUSTMENT_FUNDING_STATUS_PAYMENT_INTENT_CREATED,
    ORDER_ADJUSTMENT_FUNDING_STATUS_PAYMENT_REQUEST_CREATED,
    ORDER_ADJUSTMENT_STATUS_ACCEPTED,
    ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED,
    ORDER_ADJUSTMENT_STATUS_COUNTER_FUNDED_FINAL,
    ORDER_ADJUSTMENT_STATUS_FUNDED,
    ORDER_ADJUSTMENT_STATUS_FUNDING_PENDING,
    ORDER_COMPENSATION_ADJUSTMENT_STATUS_PENDING,
)


class AdjustmentFundingService:
    """
    Own funding workflow for accepted order adjustments.
    """

    @classmethod
    @transaction.atomic
    def create_funding_record(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        amount_expected: Decimal,
        payment_request_reference: str = "",
        invoice_reference: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentFunding:
        """
        Create the initial funding record for an accepted adjustment.
        """
        locked_request = cls._lock_request(adjustment_request)

        cls._ensure_request_can_enter_funding(locked_request)
        cls._validate_amount(amount_expected)

        existing_funding = cls._get_funding_record(locked_request)
        
        if existing_funding is not None:
            raise ValidationError(
                "Adjustment request already has a funding record."
            )

        funding = OrderAdjustmentFunding.objects.create(
            website=locked_request.website,
            adjustment_request=locked_request,
            status=ORDER_ADJUSTMENT_FUNDING_STATUS_NOT_STARTED,
            payment_request_reference=payment_request_reference,
            invoice_reference=invoice_reference,
            amount_expected=amount_expected,
            amount_paid=Decimal("0.00"),
            metadata={},
        )
        

        locked_request.status = ORDER_ADJUSTMENT_STATUS_FUNDING_PENDING
        locked_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        cls._create_event(
            adjustment_request=locked_request,
            event_type=ORDER_ADJUSTMENT_EVENT_BILLING_CREATED,
            actor=triggered_by,
            metadata={
                "funding_id": funding.pk,
                "amount_expected": str(amount_expected),
                "payment_request_reference": payment_request_reference,
                "invoice_reference": invoice_reference,
            },
        )
        return funding

    @classmethod
    @transaction.atomic
    def attach_payment_intent(
        cls,
        *,
        funding: OrderAdjustmentFunding,
        payment_intent_reference: str,
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentFunding:
        """
        Attach a payment intent reference to an existing funding record.
        """
        locked_funding = cls._lock_funding(funding)

        if not payment_intent_reference:
            raise ValidationError(
                "payment_intent_reference is required."
            )

        locked_funding.payment_intent_reference = payment_intent_reference
        locked_funding.status = (
            ORDER_ADJUSTMENT_FUNDING_STATUS_PAYMENT_INTENT_CREATED
        )
        locked_funding.save(
            update_fields=[
                "payment_intent_reference",
                "status",
                "updated_at",
            ]
        )

        cls._create_event(
            adjustment_request=locked_funding.adjustment_request,
            event_type=ORDER_ADJUSTMENT_EVENT_PAYMENT_INTENT_CREATED,
            actor=triggered_by,
            metadata={
                "funding_id": locked_funding.pk,
                "payment_intent_reference": payment_intent_reference,
            },
        )
        return locked_funding

    @classmethod
    @transaction.atomic
    def mark_payment_request_created(
        cls,
        *,
        funding: OrderAdjustmentFunding,
        payment_request_reference: str,
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentFunding:
        """
        Mark that a billing payment request was created.
        """
        locked_funding = cls._lock_funding(funding)

        if not payment_request_reference:
            raise ValidationError(
                "payment_request_reference is required."
            )

        locked_funding.payment_request_reference = payment_request_reference
        locked_funding.status = (
            ORDER_ADJUSTMENT_FUNDING_STATUS_PAYMENT_REQUEST_CREATED
        )
        locked_funding.save(
            update_fields=[
                "payment_request_reference",
                "status",
                "updated_at",
            ]
        )

        cls._create_event(
            adjustment_request=locked_funding.adjustment_request,
            event_type=ORDER_ADJUSTMENT_EVENT_BILLING_CREATED,
            actor=triggered_by,
            metadata={
                "funding_id": locked_funding.pk,
                "payment_request_reference": payment_request_reference,
            },
        )
        return locked_funding

    @classmethod
    @transaction.atomic
    def apply_payment(
        cls,
        *,
        funding: OrderAdjustmentFunding,
        amount: Decimal,
        external_reference: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderAdjustmentFunding:
        """
        Apply incoming payment to the funding record.

        Funding is only considered complete when total paid reaches or
        exceeds amount_expected.
        """
        locked_funding = cls._lock_funding(funding)
        cls._validate_amount(amount)

        new_amount_paid = locked_funding.amount_paid + amount
        locked_funding.amount_paid = new_amount_paid

        if new_amount_paid < locked_funding.amount_expected:
            locked_funding.status = (
                ORDER_ADJUSTMENT_FUNDING_STATUS_PARTIALLY_FUNDED
            )
            locked_funding.save(
                update_fields=[
                    "amount_paid",
                    "status",
                    "updated_at",
                ]
            )

            cls._create_event(
                adjustment_request=locked_funding.adjustment_request,
                event_type=(
                    ORDER_ADJUSTMENT_EVENT_PAYMENT_PARTIALLY_APPLIED
                ),
                actor=triggered_by,
                metadata={
                    "funding_id": locked_funding.pk,
                    "amount_applied": str(amount),
                    "amount_paid": str(new_amount_paid),
                    "amount_expected": str(
                        locked_funding.amount_expected
                    ),
                    "external_reference": external_reference,
                },
            )
            return locked_funding

        locked_funding.status = ORDER_ADJUSTMENT_FUNDING_STATUS_FUNDED
        locked_funding.funded_at = timezone.now()

        funded_at = locked_funding.funded_at
        assert funded_at is not None

        locked_funding.save(
            update_fields=[
                "amount_paid",
                "status",
                "funded_at",
                "updated_at",
            ]
        )

        locked_request = cls._lock_request(
            locked_funding.adjustment_request
        )
        final_status = ORDER_ADJUSTMENT_STATUS_FUNDED
        if locked_request.status == ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED:
            # If the request was client-countered, we move it to accepted
            # status instead of funded, as the client counteroffer is no
            # longer valid but the original offer is still accepted.
            final_status = ORDER_ADJUSTMENT_STATUS_COUNTER_FUNDED_FINAL
            locked_request.is_counter_final = True
            
        locked_request.status = final_status
        locked_request.funded_at = locked_funding.funded_at
        locked_request.save(
            update_fields=[
                "status",
                "updated_at",
                "is_counter_final",
                "funded_at",
            ]
        )

        cls._create_event(
            adjustment_request=locked_request,
            event_type=ORDER_ADJUSTMENT_EVENT_PAYMENT_FULLY_APPLIED,
            actor=triggered_by,
            metadata={
                "funding_id": locked_funding.pk,
                "amount_applied": str(amount),
                "amount_paid": str(new_amount_paid),
                "amount_expected": str(locked_funding.amount_expected),
                "external_reference": external_reference,
            },
        )

        cls._create_event(
            adjustment_request=locked_request,
            event_type=ORDER_ADJUSTMENT_EVENT_FUNDED,
            actor=triggered_by,
            metadata={
                "funding_id": locked_funding.pk,
                "funded_at": (
                    locked_funding.funded_at.isoformat()
                    if locked_funding.funded_at is not None
                    else ""
                ),
                "final_status": final_status,
                "amount_applied": str(amount),
                "amount_paid": str(new_amount_paid),
                "amount_expected": str(locked_funding.amount_expected),
                "external_reference": external_reference,
            
            },
        )

        AdjustmentScopeApplicationService.apply_funded_adjustment(
            adjustment_request=locked_request,
            triggered_by=triggered_by,
        )

        return locked_funding

    @classmethod
    def _create_compensation_adjustment(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        amount: Decimal,
        triggered_by: Optional[Any],
    ) -> OrderCompensationAdjustment:
        """
        Create the writer compensation adjustment placeholder after funding.
        """
        compensation = OrderCompensationAdjustment.objects.create(
            website=adjustment_request.website,
            order=adjustment_request.order,
            adjustment_request=adjustment_request,
            status=ORDER_COMPENSATION_ADJUSTMENT_STATUS_PENDING,
            adjustment_type=adjustment_request.adjustment_type,
            amount=amount,
            metadata={},
        )

        cls._create_event(
            adjustment_request=adjustment_request,
            event_type=ORDER_ADJUSTMENT_EVENT_COMPENSATION_CREATED,
            actor=triggered_by,
            metadata={
                "compensation_adjustment_id": compensation.pk,
                "amount": str(amount),
            },
        )
        return compensation

    @classmethod
    def _ensure_request_can_enter_funding(
        cls,
        adjustment_request: OrderAdjustmentRequest,
    ) -> None:
        """
        Ensure the adjustment request is accepted and ready for funding.
        The scope of the adjustment should have already been finalized
        at this point, so we only allow requests in accepted or
        client-countered status to enter funding.
        """
        if adjustment_request.status not in {
            ORDER_ADJUSTMENT_STATUS_ACCEPTED,
            ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED,
        }:
            raise ValidationError(
                "Only accepted  or client-countered adjustment requests can enter funding."
            )
        

    @classmethod
    def _validate_amount(cls, amount: Decimal) -> None:
        """
        Ensure amount is strictly positive.
        """
        if amount <= 0:
            raise ValidationError(
                "Amount must be greater than zero."
            )

    @classmethod
    def _get_funding_record(
        cls,
        adjustment_request: OrderAdjustmentRequest,
    ) -> Optional[OrderAdjustmentFunding]:
        """
        Return the existing funding record if present.
        """
        return (
            OrderAdjustmentFunding.objects.select_for_update()
            .filter(adjustment_request=adjustment_request)
            .first()
        )

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
    def _lock_funding(
        cls,
        funding: OrderAdjustmentFunding,
    ) -> OrderAdjustmentFunding:
        """
        Lock and reload a funding record inside a transaction.
        """
        return OrderAdjustmentFunding.objects.select_for_update().get(
            pk=funding.pk
        )

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