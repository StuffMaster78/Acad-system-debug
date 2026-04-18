from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from billing.constants import PaymentRequestStatus
from billing.models.payment_request import PaymentRequest
from billing.services.payment_request_service import (
    PaymentRequestService,
)
from ledger.services.payment_processor_ledger_service import (
    PaymentProcessorLedgerService,
)
from orders.models.legacy_models.order_adjustment_request import (
    OrderAdjustmentRequest,
    OrderAdjustmentStatus,
)
from orders.services.order_adjustment_billing_service import (
    OrderAdjustmentBillingService,
)
from orders.services.order_adjustment_request_service import (
    OrderAdjustmentRequestService,
)
from payments_processor.enums import PaymentIntentPurpose
from payments_processor.models import PaymentIntent
from payments_processor.services.payment_application_service import (
    PaymentApplicationService,
)
from payments_processor.services.payment_intent_service import (
    PaymentIntentService,
)


@dataclass(frozen=True)
class AdjustmentPaymentIntentResult:
    """
    Represent the outcome of preparing a billing payment request for
    settlement.

    Attributes:
        adjustment_request:
            Order adjustment request that originated the receivable.
        billing_payment_request:
            Billing payment request linked to the adjustment.
        payment_intent:
            Linked payment intent returned by payments_processor.
        provider_data:
            Provider initialization payload returned by the processor.
        created:
            Indicates whether a new payment intent was created.
    """

    adjustment_request: OrderAdjustmentRequest
    billing_payment_request: PaymentRequest
    payment_intent: PaymentIntent
    provider_data: dict[str, Any]
    created: bool


@dataclass(frozen=True)
class AdjustmentSettlementResult:
    """
    Represent the outcome of applying a verified adjustment settlement.

    Attributes:
        adjustment_request:
            Updated order adjustment request after settlement handling.
        billing_payment_request:
            Updated billing payment request after settlement handling.
        payment_intent:
            Payment intent used during settlement.
        payment_application_result:
            Raw structured result returned by
            PaymentApplicationService.apply_payment(...).
        fully_settled:
            Indicates whether the billing receivable was fully settled.
        partially_settled:
            Indicates whether settlement remains partial.
        ledger_recorded:
            Indicates whether external capture was posted to ledger.
    """

    adjustment_request: OrderAdjustmentRequest
    billing_payment_request: PaymentRequest
    payment_intent: PaymentIntent
    payment_application_result: dict[str, Any]
    fully_settled: bool
    partially_settled: bool
    ledger_recorded: bool


class OrderAdjustmentPaymentOrchestrationService:
    """
    Coordinate the end-to-end payment flow for accepted order
    adjustment requests.

    Flow:
        1. Convert accepted order adjustment to billing payment request.
        2. Create or reuse payment intent in payments_processor.
        3. Let payments_processor handle wallet or external settlement.
        4. Apply verified settlement to the billing payment request.
        5. Post external capture to ledger when applicable.
        6. Mark the order adjustment funded only after full settlement.

    Important boundary:
        This service does not perform wallet mutations directly.
        Wallet participation must happen through payments_processor
        allocations and application logic.
    """

    @staticmethod
    def _validate_adjustment_for_payment(
        *,
        adjustment_request: OrderAdjustmentRequest,
    ) -> None:
        """
        Validate that an order adjustment is ready to enter payment flow.

        Args:
            adjustment_request:
                Adjustment request being prepared for payment.

        Raises:
            ValidationError:
                Raised when the request is not in funding-pending state
                or does not have a linked billing payment request.
        """
        if adjustment_request.status not in {
            OrderAdjustmentStatus.FUNDING_PENDING,
            OrderAdjustmentStatus.ACCEPTED,
        }:
            raise ValidationError(
                "Only accepted or funding-pending adjustment requests "
                "can enter payment flow."
            )

        if (
            adjustment_request.status == OrderAdjustmentStatus.FUNDING_PENDING
            and adjustment_request.billing_payment_request is None
        ):
            raise ValidationError(
                "Funding-pending adjustment requests must have a linked "
                "billing payment request."
            )

    @staticmethod
    def _validate_billing_payment_request(
        *,
        billing_payment_request: PaymentRequest,
    ) -> None:
        """
        Validate that the billing payment request can still be settled.

        Args:
            billing_payment_request:
                Billing payment request to validate.

        Raises:
            ValidationError:
                Raised when the receivable is already terminal.
        """
        if billing_payment_request.status in {
            PaymentRequestStatus.PAID,
            PaymentRequestStatus.CANCELLED,
            PaymentRequestStatus.EXPIRED,
        }:
            raise ValidationError(
                "Only active billing payment requests can be settled."
            )

    @staticmethod
    def _get_existing_payment_intent(
        *,
        billing_payment_request: PaymentRequest,
    ) -> PaymentIntent | None:
        """
        Retrieve the currently linked payment intent for a billing
        payment request.

        Args:
            billing_payment_request:
                Billing payment request to inspect.

        Returns:
            PaymentIntent | None:
                Linked payment intent if the stored reference resolves
                successfully, otherwise None.
        """
        if not billing_payment_request.payment_intent_reference:
            return None

        try:
            return PaymentIntent.objects.get(
                reference=billing_payment_request.payment_intent_reference
            )
        except PaymentIntent.DoesNotExist:
            return None

    @staticmethod
    def _should_post_external_capture_to_ledger(
        *,
        external_reference: str | None,
        external_captured_amount: Decimal | None,
    ) -> bool:
        """
        Determine whether external capture should be posted to ledger.

        Args:
            external_reference:
                Verified external processor reference.
            external_captured_amount:
                Amount actually captured externally.

        Returns:
            bool:
                True when external settlement data is present and valid.
        """
        if not external_reference:
            return False

        if external_captured_amount is None:
            return False

        return external_captured_amount > Decimal("0")

    @classmethod
    def _post_external_capture_to_ledger(
        cls,
        *,
        billing_payment_request: PaymentRequest,
        payment_intent: PaymentIntent,
        external_reference: str,
        external_captured_amount: Decimal,
        triggered_by=None,
    ) -> None:
        """
        Post verified external capture for the billing payment request
        to ledger.

        Args:
            billing_payment_request:
                Receivable being settled.
            payment_intent:
                Payment intent tied to the external capture.
            external_reference:
                External provider or processor reference.
            external_captured_amount:
                Externally captured portion of the settlement.
            triggered_by:
                Optional actor associated with the operation.

        Raises:
            ValidationError:
                Raised when external_captured_amount is invalid.
        """
        if external_captured_amount <= Decimal("0"):
            raise ValidationError(
                "external_captured_amount must be greater than zero."
            )

        PaymentProcessorLedgerService.post_external_payment_capture(
            website=billing_payment_request.website,
            amount=external_captured_amount,
            payment_intent_reference=payment_intent.reference,
            external_reference=external_reference,
            related_object_type="billing.payment_request",
            related_object_id=str(billing_payment_request.pk),
            reference=billing_payment_request.reference,
            triggered_by=triggered_by,
            metadata={
                "billing_payment_request_id": billing_payment_request.pk,
                "payment_request_reference": (
                    billing_payment_request.reference
                ),
                "payment_request_status": billing_payment_request.status,
            },
        )

    @classmethod
    @transaction.atomic
    def ensure_billing_payment_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        requested_by=None,
        due_at=None,
        currency: str = "",
    ) -> PaymentRequest:
        """
        Ensure that an accepted adjustment request has a linked billing
        payment request.

        Args:
            adjustment_request:
                Order adjustment request to hand off into billing.
            requested_by:
                Optional actor creating the billing request.
            due_at:
                Optional due timestamp for the billing request.
            currency:
                Optional currency code.

        Returns:
            PaymentRequest:
                Existing or newly created billing payment request.
        """
        cls._validate_adjustment_for_payment(
            adjustment_request=adjustment_request
        )

        existing_request = adjustment_request.billing_payment_request
        if existing_request is not None:
            return existing_request

        return OrderAdjustmentBillingService.create_billing_payment_request(
            adjustment_request=adjustment_request,
            requested_by=requested_by,
            due_at=due_at,
            currency=currency,
        )

    @classmethod
    @transaction.atomic
    def create_payment_intent_for_adjustment(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        provider: str,
        requested_by=None,
        due_at=None,
        currency: str = "",
        reference_prefix: str = "adj",
    ) -> AdjustmentPaymentIntentResult:
        """
        Ensure billing receivable exists and create or reuse a payment
        intent for it.

        Args:
            adjustment_request:
                Order adjustment request being prepared for payment.
            provider:
                Payment provider key accepted by payments_processor.
            requested_by:
                Optional actor creating the billing request or intent.
            due_at:
                Optional due timestamp for the billing request.
            currency:
                Optional currency code for billing request creation.
            reference_prefix:
                Optional prefix used for payment intent references.

        Returns:
            AdjustmentPaymentIntentResult:
                Structured result containing the adjustment request,
                billing payment request, payment intent, and provider
                payload.

        Raises:
            ValidationError:
                Raised when adjustment or billing state is invalid.
        """
        if not provider:
            raise ValidationError("provider is required.")

        billing_payment_request = cls.ensure_billing_payment_request(
            adjustment_request=adjustment_request,
            requested_by=requested_by,
            due_at=due_at,
            currency=currency,
        )

        cls._validate_billing_payment_request(
            billing_payment_request=billing_payment_request
        )

        existing_payment_intent = cls._get_existing_payment_intent(
            billing_payment_request=billing_payment_request
        )
        if existing_payment_intent is not None:
            return AdjustmentPaymentIntentResult(
                adjustment_request=adjustment_request,
                billing_payment_request=billing_payment_request,
                payment_intent=existing_payment_intent,
                provider_data={},
                created=False,
            )

        create_result = PaymentIntentService.create_intent(
            client=billing_payment_request.client,
            provider=provider,
            purpose=PaymentIntentPurpose.BILLING_PAYMENT_REQUEST,
            amount=billing_payment_request.amount,
            currency=billing_payment_request.currency,
            payable=billing_payment_request,
            metadata={
                "order_adjustment_request_id": adjustment_request.pk,
                "billing_payment_request_id": billing_payment_request.pk,
                "payment_request_reference": (
                    billing_payment_request.reference
                ),
            },
            reference_prefix=reference_prefix,
        )

        payment_intent = create_result["payment_intent"]
        provider_data = create_result["provider_data"]

        billing_payment_request.payment_intent_reference = (
            payment_intent.reference
        )
        billing_payment_request.save(
            update_fields=["payment_intent_reference", "updated_at"]
        )

        return AdjustmentPaymentIntentResult(
            adjustment_request=adjustment_request,
            billing_payment_request=billing_payment_request,
            payment_intent=payment_intent,
            provider_data=provider_data,
            created=True,
        )

    @classmethod
    @transaction.atomic
    def apply_verified_adjustment_payment(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        payment_intent: PaymentIntent,
        total_amount: Decimal,
        external_reference: str | None = None,
        external_captured_amount: Decimal | None = None,
        triggered_by=None,
    ) -> AdjustmentSettlementResult:
        """
        Apply a verified settlement to the linked billing payment request
        and update the originating order adjustment.

        Args:
            adjustment_request:
                Order adjustment request whose receivable is settling.
            payment_intent:
                Verified payment intent linked to the billing request.
            total_amount:
                Total amount applied to the billing request.
            external_reference:
                Optional external provider reference for external capture.
            external_captured_amount:
                Optional externally captured portion of total_amount.
            triggered_by:
                Optional actor associated with the operation.

        Returns:
            AdjustmentSettlementResult:
                Structured settlement result.

        Raises:
            ValidationError:
                Raised when the linked billing request is missing or the
                payment intent does not match the billing object.
        """
        billing_payment_request = adjustment_request.billing_payment_request
        if billing_payment_request is None:
            raise ValidationError(
                "Adjustment request does not have a linked billing "
                "payment request."
            )

        cls._validate_billing_payment_request(
            billing_payment_request=billing_payment_request
        )

        if total_amount <= Decimal("0"):
            raise ValidationError(
                "total_amount must be greater than zero."
            )

        if (
            payment_intent.reference
            != billing_payment_request.payment_intent_reference
        ):
            raise ValidationError(
                "Payment intent reference does not match the billing "
                "payment request."
            )

        if payment_intent.payable_object_id != billing_payment_request.pk:
            raise ValidationError(
                "Payment intent payable does not match the billing "
                "payment request."
            )

        payment_application_result = PaymentApplicationService.apply_payment(
            payment_intent=payment_intent,
            total_amount=total_amount,
        )

        settlement_result = payment_application_result["settlement_result"]
        fully_settled = settlement_result["fully_settled"]

        if fully_settled:
            updated_payment_request = PaymentRequestService.mark_paid(
                payment_request=billing_payment_request
            )
            updated_adjustment_request = (
                OrderAdjustmentRequestService.mark_funded(
                    adjustment_request=adjustment_request,
                    reviewed_by=triggered_by,
                )
            )
        else:
            updated_payment_request = (
                PaymentRequestService.mark_partially_paid(
                    payment_request=billing_payment_request
                )
            )
            updated_adjustment_request = adjustment_request

        ledger_recorded = False

        if cls._should_post_external_capture_to_ledger(
            external_reference=external_reference,
            external_captured_amount=external_captured_amount,
        ):
            cls._post_external_capture_to_ledger(
                billing_payment_request=updated_payment_request,
                payment_intent=payment_intent,
                external_reference=external_reference or "",
                external_captured_amount=(
                    external_captured_amount or Decimal("0")
                ),
                triggered_by=triggered_by,
            )
            ledger_recorded = True

        return AdjustmentSettlementResult(
            adjustment_request=updated_adjustment_request,
            billing_payment_request=updated_payment_request,
            payment_intent=payment_intent,
            payment_application_result=payment_application_result,
            fully_settled=fully_settled,
            partially_settled=not fully_settled,
            ledger_recorded=ledger_recorded,
        )