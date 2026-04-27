from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from billing.constants import PaymentRequestStatus
from billing.models.payment_request import PaymentRequest
from billing.selectors.payment_request_selectors import (
    PaymentRequestSelector,
)
from billing.services.payment_request_service import (
    PaymentRequestService,
)
from ledger.services.payment_processor_ledger_service import (
    PaymentProcessorLedgerService,
)
from notifications_system.services.notification_service import (
    NotificationService,
)
from payments_processor.enums import PaymentIntentPurpose
from payments_processor.models import PaymentIntent
from payments_processor.services.payment_application_service import (
    PaymentApplicationService,
)
from payments_processor.services.payment_intent_service import (
    PaymentIntentService,
)
from billing.services.receipt_orchestration_service import (
    ReceiptOrchestrationService,
)
from billing.services.reminder_orchestration_service import (
            ReminderOrchestrationService,
)


@dataclass(frozen=True)
class PaymentRequestIntentPreparationResult:
    """
    Represent the outcome of preparing a billing payment request for
    payment.

    Attributes:
        payment_request:
            Updated billing payment request after preparation.
        payment_intent:
            Linked payment intent returned by payments_processor.
        provider_data:
            Provider initialization payload returned by the processor.
        created:
            Indicates whether a new payment intent was created.
    """

    payment_request: PaymentRequest
    payment_intent: PaymentIntent
    provider_data: dict[str, Any]
    created: bool


@dataclass(frozen=True)
class PaymentRequestSettlementResult:
    """
    Represent the outcome of applying a verified payment request
    settlement.

    Attributes:
        payment_request:
            Updated payment request after settlement handling.
        payment_intent:
            Payment intent used during settlement.
        payment_application_result:
            Raw structured result returned by
            PaymentApplicationService.apply_payment(...).
        fully_settled:
            Indicates whether the payment request was fully settled.
        partially_settled:
            Indicates whether the payment request remains partially
            settled.
        ledger_recorded:
            Indicates whether external capture was posted to ledger.
    """

    payment_request: PaymentRequest
    payment_intent: PaymentIntent
    payment_application_result: dict[str, Any]
    fully_settled: bool
    partially_settled: bool
    ledger_recorded: bool


class PaymentRequestOrchestrationService:
    """
    Coordinate billing payment request flows across billing,
    payments_processor, ledger, and notifications.

    Domain boundaries:
        billing:
            Owns payment request state and customer-facing receivables.

        payments_processor:
            Owns payment intent creation, provider initialization,
            verification, allocation, and settlement application.

        ledger:
            Owns financial recording of actual money movement after
            verified settlement.

        notifications_system:
            Owns delivery of billing-related notifications.
    """

    @staticmethod
    def _validate_payment_request_for_payment(
        *,
        payment_request: PaymentRequest,
    ) -> None:
        """
        Validate that a payment request can enter payment flow.

        Args:
            payment_request:
                Payment request instance to validate.

        Raises:
            ValidationError:
                Raised when the payment request is terminal or lacks a
                resolvable recipient path.
        """
        if payment_request.status in {
            PaymentRequestStatus.PAID,
            PaymentRequestStatus.CANCELLED,
            PaymentRequestStatus.EXPIRED,
        }:
            raise ValidationError(
                "Only active payment requests can be prepared for "
                "payment."
            )

        recipient_email = PaymentRequestSelector.get_recipient_email(
            payment_request=payment_request
        )
        if not recipient_email:
            raise ValidationError(
                "Payment request must have a resolvable recipient "
                "email."
            )

        if payment_request.client is None:
            raise ValidationError(
                "Payment request payment intents currently require a "
                "linked client."
            )

    @staticmethod
    def _validate_verified_payment_inputs(
        *,
        payment_request: PaymentRequest,
        payment_intent: PaymentIntent,
        total_amount: Decimal,
    ) -> None:
        """
        Validate inputs before applying a verified payment request
        payment.

        Args:
            payment_request:
                Payment request being settled.
            payment_intent:
                Verified payment intent that should belong to the
                payment request.
            total_amount:
                Confirmed amount to apply.

        Raises:
            ValidationError:
                Raised when amount is invalid or the payment intent does
                not match the payment request.
        """
        if total_amount <= Decimal("0"):
            raise ValidationError(
                "total_amount must be greater than zero."
            )

        if (
            payment_intent.reference
            != payment_request.payment_intent_reference
        ):
            raise ValidationError(
                "Payment intent reference does not match the payment "
                "request."
            )

        if payment_intent.payable_object_id != payment_request.pk:
            raise ValidationError(
                "Payment intent payable does not match the payment "
                "request."
            )

    @staticmethod
    def _get_existing_payment_intent(
        *,
        payment_request: PaymentRequest,
    ) -> PaymentIntent | None:
        """
        Retrieve the currently linked payment intent for a payment
        request.

        Args:
            payment_request:
                Payment request instance to inspect.

        Returns:
            PaymentIntent | None:
                Linked payment intent if found, otherwise None.
        """
        if not payment_request.payment_intent_reference:
            return None

        try:
            return PaymentIntent.objects.get(
                reference=payment_request.payment_intent_reference
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
        payment_request: PaymentRequest,
        payment_intent: PaymentIntent,
        external_reference: str,
        external_captured_amount: Decimal,
        triggered_by=None,
    ) -> None:
        """
        Post verified external capture for a payment request to ledger.

        Args:
            payment_request:
                Billing payment request being settled.
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
            website=payment_request.website,
            amount=external_captured_amount,
            payment_intent_reference=payment_intent.reference,
            external_reference=external_reference,
            related_object_type="billing.payment_request",
            related_object_id=str(payment_request.pk),
            reference=payment_request.reference,
            triggered_by=triggered_by,
            metadata={
                "payment_request_id": payment_request.pk,
                "payment_request_reference": payment_request.reference,
                "payment_request_status": payment_request.status,
                "payment_request_purpose": payment_request.purpose,
            },
        )

    @classmethod
    @transaction.atomic
    def create_payment_intent_for_payment_request(
        cls,
        *,
        payment_request: PaymentRequest,
        provider: str,
        reference_prefix: str = "bpr",
        triggered_by=None,
    ) -> PaymentRequestIntentPreparationResult:
        """
        Create or reuse a provider-initialized payment intent for a
        billing payment request.

        Args:
            payment_request:
                Payment request being prepared for payment.
            provider:
                Payment provider key accepted by payments_processor.
            reference_prefix:
                Optional prefix used for generated payment references.
            triggered_by:
                Optional actor associated with the action.

        Returns:
            PaymentRequestIntentPreparationResult:
                Structured result containing the payment request,
                payment intent, provider payload, and creation flag.

        Raises:
            ValidationError:
                Raised when payment request state is invalid or provider
                is blank.
        """
        cls._validate_payment_request_for_payment(
            payment_request=payment_request
        )

        if not provider:
            raise ValidationError("provider is required.")

        existing_payment_intent = cls._get_existing_payment_intent(
            payment_request=payment_request
        )
        if existing_payment_intent is not None:
            return PaymentRequestIntentPreparationResult(
                payment_request=payment_request,
                payment_intent=existing_payment_intent,
                provider_data={},
                created=False,
            )

        create_result = PaymentIntentService.create_intent(
            client=payment_request.client,
            provider=provider,
            purpose=PaymentIntentPurpose.BILLING_PAYMENT_REQUEST,
            amount=payment_request.amount,
            currency=payment_request.currency,
            payable=payment_request,
            metadata={
                "payment_request_id": payment_request.pk,
                "payment_request_reference": payment_request.reference,
                "payment_request_title": payment_request.title,
                "payment_request_status": payment_request.status,
                "recipient_email": (
                    PaymentRequestSelector.get_recipient_email(
                        payment_request=payment_request
                    )
                ),
            },
            reference_prefix=reference_prefix,
        )

        payment_intent = create_result["payment_intent"]
        provider_data = create_result["provider_data"]

        payment_request.payment_intent_reference = (
            payment_intent.reference
        )
        payment_request.save(
            update_fields=["payment_intent_reference", "updated_at"]
        )

        if triggered_by and payment_request.client:
            NotificationService.notify(
                event_key="billing.payment_request.payment_intent_created",
                recipient=payment_request.client,
                website=payment_request.website,
                triggered_by=triggered_by,
                is_silent=True,
                context={
                    "payment_request_id": payment_request.pk,
                    "payment_request_reference": payment_request.reference,
                    "payment_intent_reference": payment_intent.reference,
                    "provider": provider,
                },
            )

        return PaymentRequestIntentPreparationResult(
            payment_request=payment_request,
            payment_intent=payment_intent,
            provider_data=provider_data,
            created=True,
        )

    @classmethod
    @transaction.atomic
    def issue_payment_request_and_prepare_payment(
        cls,
        *,
        payment_request: PaymentRequest,
        provider: str,
        generate_token: bool = True,
        token_expiry_hours: int = 72,
        send_notification: bool = False,
        triggered_by=None,
    ) -> PaymentRequestIntentPreparationResult:
        """
        Issue a payment request and ensure a payment intent exists.

        Args:
            payment_request:
                Billing payment request to prepare.
            provider:
                Payment provider key accepted by payments_processor.
            send_notification:
                Whether to emit a customer-facing issue event.
            triggered_by:
                Optional actor initiating the operation.

        Returns:
            PaymentRequestIntentPreparationResult:
                Structured result containing the updated payment request
                and linked payment intent.
        """
        prepared_request = payment_request

        if prepared_request.status == PaymentRequestStatus.DRAFT:
            prepared_request = PaymentRequestService.issue_payment_request(
                payment_request=prepared_request
            )

        if generate_token:
            prepared_request = PaymentRequestService.ensure_payment_token(
                payment_request=prepared_request,
                expiry_hours=token_expiry_hours,
            )

        result = cls.create_payment_intent_for_payment_request(
            payment_request=prepared_request,
            provider=provider,
            triggered_by=triggered_by,
        )

        scheduled_for = ReminderOrchestrationService.suggest_default_schedule(
            due_at=result.payment_request.due_at
        )

        if scheduled_for is not None:
            ReminderOrchestrationService.schedule_payment_request_reminder(
                payment_request=result.payment_request,
                scheduled_for=scheduled_for,
            )

        if send_notification and result.payment_request.client:
            NotificationService.notify(
                event_key="billing.payment_request.issued",
                recipient=result.payment_request.client,
                website=result.payment_request.website,
                triggered_by=triggered_by,
                context={
                    "payment_request_id": result.payment_request.pk,
                    "payment_request_reference": (
                        result.payment_request.reference
                    ),
                    "payment_request_title": result.payment_request.title,
                    "payment_request_amount": str(
                        result.payment_request.amount
                    ),
                    "payment_request_currency": (
                        result.payment_request.currency
                    ),
                    "payment_request_due_at": (
                        result.payment_request.due_at.isoformat()
                        if result.payment_request.due_at is not None
                        else ""
                    ),
                    "payment_intent_reference": (
                        result.payment_intent.reference
                    ),
                    "provider": provider,
                },
            )

        return result

    @classmethod
    @transaction.atomic
    def apply_verified_payment_request_payment(
        cls,
        *,
        payment_request: PaymentRequest,
        payment_intent: PaymentIntent,
        total_amount: Decimal,
        external_reference: str | None = None,
        external_captured_amount: Decimal | None = None,
        send_notification: bool = False,
        triggered_by=None,
    ) -> PaymentRequestSettlementResult:
        """
        Apply a verified payment to a billing payment request and
        optionally post external capture to ledger.

        Args:
            payment_request:
                Billing payment request being settled.
            payment_intent:
                Verified payment intent linked to the payment request.
            total_amount:
                Total confirmed amount applied to the payment request.
            external_reference:
                Optional external provider reference.
            external_captured_amount:
                Optional externally captured portion of total_amount.
            send_notification:
                Whether to emit a settlement event.
            triggered_by:
                Optional actor associated with the operation.

        Returns:
            PaymentRequestSettlementResult:
                Structured settlement result.

        Raises:
            ValidationError:
                Raised when payment request cannot be settled or inputs
                are inconsistent.
        """
        cls._validate_payment_request_for_payment(
            payment_request=payment_request
        )
        cls._validate_verified_payment_inputs(
            payment_request=payment_request,
            payment_intent=payment_intent,
            total_amount=total_amount,
        )

        payment_application_result = PaymentApplicationService.apply_payment(
            payment_intent=payment_intent,
            total_amount=total_amount,
        )

        settlement_result = payment_application_result["settlement_result"]
        fully_settled = settlement_result["fully_settled"]

        if fully_settled:
            updated_request = PaymentRequestService.mark_paid(
                payment_request=payment_request
            )

            # Issue receipt (side-effect)
            ReceiptOrchestrationService.issue_receipt_for_payment_request(
                payment_request=updated_request,
                amount=total_amount,
                payment_intent_reference=payment_intent.reference,
                external_reference=external_reference or "",
                payment_provider=payment_intent.provider,
                send_email=True,
                triggered_by=triggered_by,
            )

            # Cancel pending reminders
            ReminderOrchestrationService.cancel_pending_reminders_for_payment_request(
                payment_request=updated_request
            )
        else:
            updated_request = PaymentRequestService.mark_partially_paid(
                payment_request=payment_request
            )

        ledger_recorded = False

        if cls._should_post_external_capture_to_ledger(
            external_reference=external_reference,
            external_captured_amount=external_captured_amount,
        ):
            cls._post_external_capture_to_ledger(
                payment_request=updated_request,
                payment_intent=payment_intent,
                external_reference=external_reference or "",
                external_captured_amount=(
                    external_captured_amount or Decimal("0")
                ),
                triggered_by=triggered_by,
            )
            ledger_recorded = True

        if send_notification and updated_request.client:
            NotificationService.notify(
                event_key="billing.payment_request.settled",
                recipient=updated_request.client,
                website=updated_request.website,
                triggered_by=triggered_by,
                context={
                    "payment_request_id": updated_request.pk,
                    "payment_request_reference": (
                        updated_request.reference
                    ),
                    "payment_request_title": updated_request.title,
                    "payment_request_amount": str(updated_request.amount),
                    "payment_request_currency": updated_request.currency,
                    "settled_amount": str(total_amount),
                    "payment_request_status": updated_request.status,
                    "payment_intent_reference": payment_intent.reference,
                    "fully_settled": fully_settled,
                    "ledger_recorded": ledger_recorded,
                },
            )

        return PaymentRequestSettlementResult(
            payment_request=updated_request,
            payment_intent=payment_intent,
            payment_application_result=payment_application_result,
            fully_settled=fully_settled,
            partially_settled=not fully_settled,
            ledger_recorded=ledger_recorded,
        )