from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from billing.services.payment_request_service import (
    PaymentRequestService,
)
from orders.models.legacy_models.order_adjustment_request import (
    OrderAdjustmentRequest,
    OrderAdjustmentStatus,
)
from orders.services.order_adjustment_request_service import (
    OrderAdjustmentRequestService,
)


class OrderAdjustmentBillingService:
    """
    Bridge accepted order adjustment requests into billing payment
    requests.

    This service coordinates handoff from the orders domain into the
    billing domain after commercial terms are finalized.

    Responsibilities:
        1. Validate adjustment request readiness for billing.
        2. Create a billing payment request from the adjustment.
        3. Link the billing record back to the adjustment request.
        4. Move the adjustment request into funding-pending state.

    Non-responsibilities:
        1. It does not negotiate adjustment terms.
        2. It does not issue invoices.
        3. It does not create payment intents.
        4. It does not collect money.
        5. It does not post to ledger.
    """

    @staticmethod
    def _validate_adjustment_for_billing(
        *,
        adjustment_request: OrderAdjustmentRequest,
    ) -> None:
        """
        Validate that an adjustment request is ready to create a billing
        payment request.

        Args:
            adjustment_request:
                Adjustment request being handed off to billing.

        Raises:
            ValidationError:
                Raised when the request is not accepted, has no final
                amount, or already has a billing artifact.
        """
        if adjustment_request.status != OrderAdjustmentStatus.ACCEPTED:
            raise ValidationError(
                "Only accepted adjustment requests can create a "
                "billing payment request."
            )

        if adjustment_request.final_amount is None:
            raise ValidationError(
                "Accepted adjustment requests must have a final_amount."
            )

        if adjustment_request.final_amount <= 0:
            raise ValidationError(
                "final_amount must be greater than zero."
            )

        if adjustment_request.billing_payment_request is not None:
            raise ValidationError(
                "A billing payment request is already linked to this "
                "adjustment request."
            )

        if adjustment_request.invoice is not None:
            raise ValidationError(
                "An invoice is already linked to this adjustment "
                "request."
            )

    @staticmethod
    def _build_payment_request_title(
        *,
        adjustment_request: OrderAdjustmentRequest,
    ) -> str:
        """
        Build a customer-facing billing title for the adjustment.

        Args:
            adjustment_request:
                Accepted adjustment request.

        Returns:
            str:
                Human-readable payment request title.
        """
        return adjustment_request.title

    @staticmethod
    def _build_payment_request_description(
        *,
        adjustment_request: OrderAdjustmentRequest,
    ) -> str:
        """
        Build a billing description from the adjustment request.

        Args:
            adjustment_request:
                Accepted adjustment request.

        Returns:
            str:
                Customer-facing payment request description.
        """
        if adjustment_request.description:
            return adjustment_request.description

        return (
            "Payment required for an approved order adjustment request."
        )

    @classmethod
    @transaction.atomic
    def create_billing_payment_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        requested_by=None,
        due_at=None,
        currency: str = "",
    ):
        """
        Create a billing payment request from an accepted order
        adjustment request.

        Args:
            adjustment_request:
                Accepted adjustment request to hand off into billing.
            requested_by:
                Optional actor creating the billing request.
            due_at:
                Optional due timestamp for the billing request.
            currency:
                Optional currency code for the billing request.

        Returns:
            PaymentRequest:
                Newly created billing payment request.

        Raises:
            ValidationError:
                Raised when the adjustment request is not ready for
                billing.
        """
        cls._validate_adjustment_for_billing(
            adjustment_request=adjustment_request
        )

        order = adjustment_request.order
        client = getattr(order, "client", None)
        final_amount = adjustment_request.final_amount

        if final_amount is None:
            raise ValidationError(
                "Accepted adjustment request must have a final_amount."
            )
        
        billing_payment_request = (
            PaymentRequestService.create_payment_request(
                website=adjustment_request.website,
                title=cls._build_payment_request_title(
                    adjustment_request=adjustment_request
                ),
                amount=final_amount,
                requested_by=requested_by,
                purpose="order",
                description=cls._build_payment_request_description(
                    adjustment_request=adjustment_request
                ),
                client=client,
                recipient_email=getattr(client, "email", ""),
                recipient_name=(
                    client.get_full_name()
                    if client is not None
                    and hasattr(client, "get_full_name")
                    else ""
                ),
                order=order,
                due_at=due_at,
                currency=currency,
            )
        )

        OrderAdjustmentRequestService.mark_funding_pending(
            adjustment_request=adjustment_request,
            billing_payment_request=billing_payment_request,
            reviewed_by=requested_by,
        )

        return billing_payment_request