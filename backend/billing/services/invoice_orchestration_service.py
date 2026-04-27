from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from billing.models.invoice import Invoice, InvoiceStatus
from billing.selectors.invoice_selectors import InvoiceSelector
from billing.services.invoice_service import InvoiceService
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
from billing.services.installment_allocation_service import (
    InstallmentAllocationService,
)


@dataclass(frozen=True)
class InvoiceIntentPreparationResult:
    """
    Represent the outcome of preparing an invoice for payment.

    Attributes:
        invoice:
            Updated invoice instance after preparation.
        payment_intent:
            Linked payment intent returned by payments_processor.
        provider_data:
            Provider initialization payload returned by the processor.
            This is usually consumed by the API layer or frontend.
        created:
            Indicates whether a new payment intent was created.
            False means an existing valid intent was reused.
    """

    invoice: Invoice
    payment_intent: PaymentIntent
    provider_data: dict[str, Any]
    created: bool


@dataclass(frozen=True)
class InvoiceSettlementResult:
    """
    Represent the outcome of applying a verified invoice payment.

    Attributes:
        invoice:
            Updated invoice after settlement handling.
        payment_intent:
            Payment intent used during settlement.
        payment_application_result:
            Raw structured result returned by
            PaymentApplicationService.apply_payment(...).
        fully_settled:
            Indicates whether the invoice was fully settled.
        partially_settled:
            Indicates whether the invoice remains only partially settled.
        ledger_recorded:
            Indicates whether external capture was posted to ledger.
    """

    invoice: Invoice
    payment_intent: PaymentIntent
    payment_application_result: dict[str, Any]
    fully_settled: bool
    partially_settled: bool
    ledger_recorded: bool


class InvoiceOrchestrationService:
    """
    Coordinate invoice flows across billing, payments_processor,
    ledger, and notifications.

    Domain boundaries:
        billing:
            Owns invoice state, recipient information, and customer-facing
            billing records.

        payments_processor:
            Owns payment intent creation, provider initialization,
            verification, allocation, and settlement application.

        ledger:
            Owns the financial record of actual money movement.
            It should only be written to after verified settlement.

        notifications_system:
            Owns delivery of billing-related notifications.

    Responsibilities:
        1. Validate whether an invoice can enter payment flow.
        2. Create or reuse a payment intent for an invoice.
        3. Issue invoices and generate payment access when required.
        4. Apply verified payments through payments_processor.
        5. Update invoice state after settlement.
        6. Post external capture to ledger when applicable.
        7. Emit notification events for important lifecycle actions.

    Non-responsibilities:
        1. This service does not talk to providers directly.
        2. This service does not replace PaymentIntentService.
        3. This service does not replace PaymentApplicationService.
        4. This service does not perform receipt generation.
        5. This service does not handle wallet-side ledger posting.
    """

    @staticmethod
    def _validate_invoice_for_payment(*, invoice: Invoice) -> None:
        """
        Validate that an invoice is eligible to enter payment flow.

        Args:
            invoice:
                Invoice instance to validate.

        Raises:
            ValidationError:
                Raised when the invoice is in a terminal state or
                cannot resolve a payable recipient.
        """
        if invoice.status in {
            InvoiceStatus.PAID,
            InvoiceStatus.CANCELLED,
            InvoiceStatus.EXPIRED,
        }:
            raise ValidationError(
                "Only active invoices can be prepared for payment."
            )

        recipient_email = InvoiceSelector.get_recipient_email(invoice=invoice)
        if not recipient_email:
            raise ValidationError(
                "Invoice must have a resolvable recipient email."
            )

        if invoice.client is None:
            raise ValidationError(
                "Invoice payment intents currently require a linked client."
            )

    @staticmethod
    def _validate_verified_payment_inputs(
        *,
        invoice: Invoice,
        payment_intent: PaymentIntent,
        total_amount: Decimal,
    ) -> None:
        """
        Validate core inputs before applying a verified invoice payment.

        Args:
            invoice:
                Invoice being settled.
            payment_intent:
                Verified payment intent that should belong to the invoice.
            total_amount:
                Confirmed amount to apply.

        Raises:
            ValidationError:
                Raised when the amount is invalid or the payment intent
                does not match the invoice.
        """
        if total_amount <= Decimal("0"):
            raise ValidationError(
                "total_amount must be greater than zero."
            )

        if payment_intent.reference != invoice.payment_intent_reference:
            raise ValidationError(
                "Payment intent reference does not match the invoice."
            )

        if payment_intent.payable_object_id != invoice.pk:
            raise ValidationError(
                "Payment intent payable does not match the invoice."
            )

    @staticmethod
    def _get_existing_payment_intent(
        *,
        invoice: Invoice,
    ) -> PaymentIntent | None:
        """
        Retrieve the currently linked payment intent for an invoice.

        Args:
            invoice:
                Invoice instance to inspect.

        Returns:
            PaymentIntent | None:
                Linked payment intent if the stored reference resolves
                successfully, otherwise None.

        Notes:
            This method is intentionally tolerant of stale references.
            That makes the orchestration layer more resilient while the
            system is still being refactored.
        """
        if not invoice.payment_intent_reference:
            return None

        try:
            return PaymentIntent.objects.get(
                reference=invoice.payment_intent_reference
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
        Determine whether an external capture should be posted to ledger.

        Args:
            external_reference:
                Verified provider or processor reference for the external
                capture event.
            external_captured_amount:
                Amount actually captured externally.

        Returns:
            bool:
                True when external settlement data is present and suitable
                for ledger posting, otherwise False.
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
        invoice: Invoice,
        payment_intent: PaymentIntent,
        external_reference: str,
        external_captured_amount: Decimal,
        triggered_by=None,
    ) -> None:
        """
        Post verified external capture for an invoice to ledger.

        Args:
            invoice:
                Invoice whose settlement is being recorded.
            payment_intent:
                Payment intent tied to the external capture.
            external_reference:
                Provider or processor reference for the external capture.
            external_captured_amount:
                Amount actually captured externally.
            triggered_by:
                Optional actor associated with the action.

        Raises:
            ValidationError:
                Raised when the external captured amount is invalid.
        """
        if external_captured_amount <= Decimal("0"):
            raise ValidationError(
                "external_captured_amount must be greater than zero."
            )

        PaymentProcessorLedgerService.post_external_payment_capture(
            website=invoice.website,
            amount=external_captured_amount,
            payment_intent_reference=payment_intent.reference,
            external_reference=external_reference,
            related_object_type="billing.invoice",
            related_object_id=str(invoice.pk),
            reference=invoice.reference,
            triggered_by=triggered_by,
            metadata={
                "invoice_id": invoice.pk,
                "invoice_reference": invoice.reference,
                "invoice_status": invoice.status,
                "invoice_purpose": invoice.purpose,
            },
        )

    @classmethod
    @transaction.atomic
    def create_payment_intent_for_invoice(
        cls,
        *,
        invoice: Invoice,
        provider: str,
        reference_prefix: str = "inv",
        triggered_by=None,
    ) -> InvoiceIntentPreparationResult:
        """
        Create a provider initialized payment intent for an invoice.

        This method only creates a new payment intent when the invoice
        does not already have a valid linked intent reference.

        Args:
            invoice:
                Invoice being prepared for payment.
            provider:
                Payment provider key accepted by PaymentIntentService.
            reference_prefix:
                Optional prefix used when generating payment intent
                references.
            triggered_by:
                Optional actor associated with the action.

        Returns:
            InvoiceIntentPreparationResult:
                Structured result containing the invoice, payment intent,
                provider payload, and a creation flag.

        Raises:
            ValidationError:
                Raised when the invoice is not eligible for payment flow
                or when provider is blank.
        """
        cls._validate_invoice_for_payment(invoice=invoice)

        if not provider:
            raise ValidationError("provider is required.")

        existing_payment_intent = cls._get_existing_payment_intent(
            invoice=invoice
        )
        if existing_payment_intent is not None:
            return InvoiceIntentPreparationResult(
                invoice=invoice,
                payment_intent=existing_payment_intent,
                provider_data={},
                created=False,
            )

        create_result = PaymentIntentService.create_intent(
            client=invoice.client,
            provider=provider,
            purpose=PaymentIntentPurpose.INVOICE,
            amount=invoice.amount,
            currency=invoice.currency,
            payable=invoice,
            metadata={
                "invoice_id": invoice.pk,
                "invoice_reference": invoice.reference,
                "invoice_title": invoice.title,
                "invoice_status": invoice.status,
                "recipient_email": InvoiceSelector.get_recipient_email(
                    invoice=invoice
                ),
            },
            reference_prefix=reference_prefix,
        )

        payment_intent = create_result["payment_intent"]
        provider_data = create_result["provider_data"]

        updated_invoice = InvoiceService.attach_payment_intent_reference(
            invoice=invoice,
            payment_intent_reference=payment_intent.reference,
        )

        if triggered_by and updated_invoice.client:
            NotificationService.notify(
                event_key="billing.invoice.payment_intent_created",
                recipient=updated_invoice.client,
                website=updated_invoice.website,
                triggered_by=triggered_by,
                is_silent=True,
                context={
                    "invoice_id": updated_invoice.pk,
                    "invoice_reference": updated_invoice.reference,
                    "payment_intent_reference": payment_intent.reference,
                    "provider": provider,
                },
            )

        return InvoiceIntentPreparationResult(
            invoice=updated_invoice,
            payment_intent=payment_intent,
            provider_data=provider_data,
            created=True,
        )

    @classmethod
    @transaction.atomic
    def issue_invoice_and_prepare_payment(
        cls,
        *,
        invoice: Invoice,
        provider: str,
        generate_token: bool = True,
        token_expiry_hours: int = 72,
        send_notification: bool = False,
        triggered_by=None,
    ) -> InvoiceIntentPreparationResult:
        """
        Issue an invoice, optionally generate a token, and ensure a
        payment intent exists.

        This is the main path for taking a draft invoice and making it
        ready for customer payment.

        Args:
            invoice:
                Invoice to prepare.
            provider:
                Payment provider key accepted by PaymentIntentService.
            generate_token:
                Whether to ensure a payment token exists.
            token_expiry_hours:
                Expiry duration for generated token access.
            send_notification:
                Whether to emit a customer-facing issue event.
            triggered_by:
                Optional actor initiating the operation.

        Returns:
            InvoiceIntentPreparationResult:
                Structured result containing the updated invoice and
                linked payment intent.
        """
        prepared_invoice = invoice

        if prepared_invoice.status == InvoiceStatus.DRAFT:
            prepared_invoice = InvoiceService.issue_invoice(
                invoice=prepared_invoice
            )

        if generate_token:
            prepared_invoice = InvoiceService.ensure_payment_token(
                invoice=prepared_invoice,
                expiry_hours=token_expiry_hours,
            )

        result = cls.create_payment_intent_for_invoice(
            invoice=prepared_invoice,
            provider=provider,
            triggered_by=triggered_by,
        )

        scheduled_for = ReminderOrchestrationService.suggest_default_schedule(
            due_at=result.invoice.due_at
        )

        if scheduled_for is not None:
            ReminderOrchestrationService.schedule_invoice_reminder(
                invoice=result.invoice,
                scheduled_for=scheduled_for,
            )

        if send_notification and result.invoice.client:
            NotificationService.notify(
                event_key="billing.invoice.issued",
                recipient=result.invoice.client,
                website=result.invoice.website,
                triggered_by=triggered_by,
                context={
                    "invoice_id": result.invoice.pk,
                    "invoice_reference": result.invoice.reference,
                    "invoice_title": result.invoice.title,
                    "invoice_amount": str(result.invoice.amount),
                    "invoice_currency": result.invoice.currency,
                    "invoice_due_at": result.invoice.due_at.isoformat(),
                    "payment_token": result.invoice.payment_token,
                    "payment_intent_reference": (
                        result.payment_intent.reference
                    ),
                    "provider": provider,
                },
            )

        return result

    @classmethod
    @transaction.atomic
    def apply_verified_invoice_payment(
        cls,
        *,
        invoice: Invoice,
        payment_intent: PaymentIntent,
        total_amount: Decimal,
        external_reference: str | None = None,
        external_captured_amount: Decimal | None = None,
        send_notification: bool = False,
        triggered_by=None,
    ) -> InvoiceSettlementResult:
        """
        Apply a verified invoice payment and optionally post external
        capture to ledger.

        This method assumes payment verification has already happened
        in payments_processor. It coordinates settlement application,
        invoice state updates, optional ledger recording, and optional
        notification emission.

        Args:
            invoice:
                Invoice being settled.
            payment_intent:
                Verified payment intent linked to the invoice.
            total_amount:
                Total confirmed amount applied to the invoice.
            external_reference:
                Optional external provider reference for the externally
                captured portion of the payment.
            external_captured_amount:
                Optional externally captured portion of the payment.
                This is especially useful for split payment scenarios
                where only part of the total was paid externally.
            send_notification:
                Whether to emit a billing settlement event.
            triggered_by:
                Optional actor associated with the operation.

        Returns:
            InvoiceSettlementResult:
                Structured settlement result including invoice state,
                processor output, and ledger recording flag.

        Raises:
            ValidationError:
                Raised when the invoice cannot be settled or input
                values are inconsistent.
        """
        cls._validate_invoice_for_payment(invoice=invoice)
        cls._validate_verified_payment_inputs(
            invoice=invoice,
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
            updated_invoice = InvoiceService.mark_paid(invoice=invoice)

            # Allocate the installment
            InstallmentAllocationService.allocate_payment_to_invoice_installments(
                invoice=updated_invoice,
                amount=total_amount,
            )

            # Issue receipt (side-effect)
            ReceiptOrchestrationService.issue_receipt_for_invoice(
                invoice=updated_invoice,
                amount=total_amount,
                payment_intent_reference=payment_intent.reference,
                external_reference=external_reference or "",
                payment_provider=payment_intent.provider,
                send_email=True,
                triggered_by=triggered_by,
            )

            # Cancel any pending reminders
            ReminderOrchestrationService.cancel_pending_reminders_for_invoice(
                invoice=updated_invoice
            )
        else:
            updated_invoice = InvoiceService.mark_partially_paid(
                invoice=invoice
            )

            InstallmentAllocationService.allocate_payment_to_invoice_installments(
                invoice=updated_invoice,
                amount=total_amount,
            )

        ledger_recorded = False

        if cls._should_post_external_capture_to_ledger(
            external_reference=external_reference,
            external_captured_amount=external_captured_amount,
        ):
            cls._post_external_capture_to_ledger(
                invoice=updated_invoice,
                payment_intent=payment_intent,
                external_reference=external_reference or "",
                external_captured_amount=(
                    external_captured_amount or Decimal("0")
                ),
                triggered_by=triggered_by,
            )
            ledger_recorded = True

        if send_notification and updated_invoice.client:
            NotificationService.notify(
                event_key="billing.invoice.settled",
                recipient=updated_invoice.client,
                website=updated_invoice.website,
                triggered_by=triggered_by,
                context={
                    "invoice_id": updated_invoice.pk,
                    "invoice_reference": updated_invoice.reference,
                    "invoice_title": updated_invoice.title,
                    "invoice_amount": str(updated_invoice.amount),
                    "invoice_currency": updated_invoice.currency,
                    "settled_amount": str(total_amount),
                    "invoice_status": updated_invoice.status,
                    "payment_intent_reference": payment_intent.reference,
                    "fully_settled": fully_settled,
                    "ledger_recorded": ledger_recorded,
                },
            )

        return InvoiceSettlementResult(
            invoice=updated_invoice,
            payment_intent=payment_intent,
            payment_application_result=payment_application_result,
            fully_settled=fully_settled,
            partially_settled=not fully_settled,
            ledger_recorded=ledger_recorded,
        )

    @classmethod
    @transaction.atomic
    def refresh_invoice_payment_access(
        cls,
        *,
        invoice: Invoice,
        provider: str,
        token_expiry_hours: int = 72,
        triggered_by=None,
    ) -> InvoiceIntentPreparationResult:
        """
        Refresh invoice payment access by regenerating token and ensuring
        a payment intent is available.

        Args:
            invoice:
                Invoice to refresh.
            provider:
                Payment provider key accepted by PaymentIntentService.
            token_expiry_hours:
                Expiry duration for regenerated token access.
            triggered_by:
                Optional actor initiating the action.

        Returns:
            InvoiceIntentPreparationResult:
                Structured result containing the refreshed invoice and
                linked payment intent.
        """
        cls._validate_invoice_for_payment(invoice=invoice)

        refreshed_invoice = InvoiceService.ensure_payment_token(
            invoice=invoice,
            expiry_hours=token_expiry_hours,
            force_refresh=True,
        )

        return cls.create_payment_intent_for_invoice(
            invoice=refreshed_invoice,
            provider=provider,
            triggered_by=triggered_by,
        )

    @classmethod
    @transaction.atomic
    def mark_invoice_email_dispatched(
        cls,
        *,
        invoice: Invoice,
        triggered_by=None,
    ) -> Invoice:
        """
        Record invoice email delivery metadata after successful dispatch.

        Args:
            invoice:
                Invoice whose email tracking should be updated.
            triggered_by:
                Optional actor associated with the send event.

        Returns:
            Invoice:
                Updated invoice instance with incremented email tracking.
        """
        updated_invoice = InvoiceService.mark_email_sent(invoice=invoice)

        if updated_invoice.client:
            NotificationService.notify(
                event_key="billing.invoice.email_sent",
                recipient=updated_invoice.client,
                website=updated_invoice.website,
                triggered_by=triggered_by,
                is_silent=True,
                context={
                    "invoice_id": updated_invoice.pk,
                    "invoice_reference": updated_invoice.reference,
                    "email_sent_count": updated_invoice.email_sent_count,
                    "email_sent_at": (
                        updated_invoice.email_sent_at.isoformat()
                        if updated_invoice.email_sent_at
                        else ""
                    ),
                },
            )

        return updated_invoice