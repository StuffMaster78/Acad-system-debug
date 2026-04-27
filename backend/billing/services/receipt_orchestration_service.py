from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from billing.constants import ReceiptStatus
from billing.models.invoice import Invoice
from billing.models.payment_request import PaymentRequest
from billing.models.receipt import Receipt
from billing.services.receipt_service import ReceiptService
from notifications_system.services.notification_service import (
    NotificationService,
)
from billing.constants import InvoiceStatus, PaymentRequestStatus


@dataclass(frozen=True)
class ReceiptIssuanceResult:
    """
    Represent the outcome of issuing a receipt.

    Attributes:
        receipt:
            Newly issued receipt instance.
        created:
            Indicates whether a new receipt was created.
    """

    receipt: Receipt
    created: bool


class ReceiptOrchestrationService:
    """
    Coordinate receipt issuance for fully settled billing objects.

    This service creates post-settlement receipt artifacts for invoices
    and billing payment requests, avoids duplicate issuance, and emits
    tenant-aware receipt notifications.
    """

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        """
        Validate receipt amount.

        Args:
            amount:
                Amount to validate.

        Raises:
            ValidationError:
                Raised when amount is not greater than zero.
        """
        if amount <= Decimal("0"):
            raise ValidationError(
                "Receipt amount must be greater than zero."
            )

    @staticmethod
    def _validate_targets(
        *,
        invoice: Invoice | None = None,
        payment_request: PaymentRequest | None = None,
    ) -> None:
        """
        Validate receipt target selection.

        Args:
            invoice:
                Optional invoice target.
            payment_request:
                Optional billing payment request target.

        Raises:
            ValidationError:
                Raised when neither target is provided or both are
                provided.
        """
        has_invoice = invoice is not None
        has_payment_request = payment_request is not None

        if not has_invoice and not has_payment_request:
            raise ValidationError(
                "Receipt issuance requires an invoice or payment "
                "request."
            )

        if has_invoice and has_payment_request:
            raise ValidationError(
                "Receipt issuance cannot target both an invoice and a "
                "payment request."
            )

    @staticmethod
    def _validate_invoice_paid(*, invoice: Invoice) -> None:
        """
        Validate that an invoice is fully paid before issuing receipt.

        Args:
            invoice:
                Invoice to validate.

        Raises:
            ValidationError:
                Raised when invoice is not fully paid.
        """
        if invoice.status != InvoiceStatus.PAID:
            raise ValidationError(
                "Receipts may only be issued for fully paid invoices."
            )

    @staticmethod
    def _validate_payment_request_paid(
        *,
        payment_request: PaymentRequest,
    ) -> None:
        """
        Validate that a billing payment request is fully paid before
        issuing receipt.

        Args:
            payment_request:
                Payment request to validate.

        Raises:
            ValidationError:
                Raised when payment request is not fully paid.
        """
        if payment_request.status != PaymentRequestStatus.PAID:
            raise ValidationError(
                "Receipts may only be issued for fully paid payment "
                "requests."
            )

    @staticmethod
    def _get_existing_receipt_for_invoice(
        *,
        invoice: Invoice,
        payment_intent_reference: str,
        external_reference: str,
    ) -> Receipt | None:
        """
        Retrieve an existing receipt for an invoice when one already
        matches the settlement identifiers.

        Args:
            invoice:
                Invoice linked to the receipt.
            payment_intent_reference:
                Payment intent reference for settlement.
            external_reference:
                External provider reference for settlement.

        Returns:
            Receipt | None:
                Matching receipt if found, otherwise None.
        """
        queryset = Receipt.objects.filter(
            website=invoice.website,
            invoice=invoice,
            status=ReceiptStatus.ISSUED,
        )

        if payment_intent_reference:
            queryset = queryset.filter(
                payment_intent_reference=payment_intent_reference
            )

        if external_reference:
            queryset = queryset.filter(
                external_reference=external_reference
            )

        return queryset.first()

    @staticmethod
    def _get_existing_receipt_for_payment_request(
        *,
        payment_request: PaymentRequest,
        payment_intent_reference: str,
        external_reference: str,
    ) -> Receipt | None:
        """
        Retrieve an existing receipt for a payment request when one
        already matches the settlement identifiers.

        Args:
            payment_request:
                Payment request linked to the receipt.
            payment_intent_reference:
                Payment intent reference for settlement.
            external_reference:
                External provider reference for settlement.

        Returns:
            Receipt | None:
                Matching receipt if found, otherwise None.
        """
        queryset = Receipt.objects.filter(
            website=payment_request.website,
            payment_request=payment_request,
            status=ReceiptStatus.ISSUED,
        )

        if payment_intent_reference:
            queryset = queryset.filter(
                payment_intent_reference=payment_intent_reference
            )

        if external_reference:
            queryset = queryset.filter(
                external_reference=external_reference
            )

        return queryset.first()

    @staticmethod
    def _build_provider_snapshot(
        *,
        invoice: Invoice | None = None,
        payment_request: PaymentRequest | None = None,
        payment_provider: str = "",
    ) -> str:
        """
        Resolve payment provider snapshot for the receipt.

        Args:
            invoice:
                Optional invoice target.
            payment_request:
                Optional payment request target.
            payment_provider:
                Explicit provider override when available.

        Returns:
            str:
                Best available payment provider snapshot.
        """
        if payment_provider:
            return payment_provider

        if invoice is not None:
            payment_intent = getattr(invoice, "payment_intent_reference", "")
            if payment_intent:
                return ""

        if payment_request is not None:
            payment_intent = getattr(
                payment_request,
                "payment_intent_reference",
                "",
            )
            if payment_intent:
                return ""

        return ""

    @classmethod
    def _send_receipt_email(
        cls,
        *,
        receipt: Receipt,
        triggered_by=None,
    ) -> None:
        """
        Emit a receipt-issued notification for email delivery.

        Args:
            receipt:
                Issued receipt.
            triggered_by:
                Optional actor associated with the action.
        """
        recipient = receipt.client
        if recipient is None and not receipt.recipient_email:
            return

        NotificationService.notify(
            event_key="billing.receipt.issued",
            recipient=recipient,
            website=receipt.website,
            triggered_by=triggered_by,
            context={
                "receipt_id": receipt.pk,
                "receipt_reference": receipt.reference,
                "receipt_amount": str(receipt.amount),
                "receipt_currency": receipt.currency,
                "issued_at": (
                    receipt.issued_at.isoformat()
                    if receipt.issued_at is not None
                    else ""
                ),
                "recipient_email": receipt.recipient_email,
                "recipient_name": receipt.recipient_name,
                "company_name": receipt.company_name_snapshot,
                "website_name": receipt.website_name_snapshot,
                "website_domain": receipt.website_domain_snapshot,
                "support_email": receipt.support_email_snapshot,
                "title": receipt.title_snapshot,
                "description": receipt.description_snapshot,
                "payment_intent_reference": (
                    receipt.payment_intent_reference
                ),
                "external_reference": receipt.external_reference,
                "payment_provider": receipt.payment_provider,
            },
        )

    @classmethod
    @transaction.atomic
    def issue_receipt_for_invoice(
        cls,
        *,
        invoice: Invoice,
        amount: Decimal,
        payment_intent_reference: str = "",
        external_reference: str = "",
        payment_provider: str = "",
        send_email: bool = True,
        triggered_by=None,
    ) -> ReceiptIssuanceResult:
        """
        Issue a receipt for a fully paid invoice.

        Args:
            invoice:
                Fully paid invoice.
            amount:
                Settled amount acknowledged by the receipt.
            payment_intent_reference:
                Payment intent reference for settlement.
            external_reference:
                External provider reference for settlement.
            payment_provider:
                Provider used for settlement.
            send_email:
                Whether to emit receipt notification email.
            triggered_by:
                Optional actor associated with issuance.

        Returns:
            ReceiptIssuanceResult:
                Structured result containing the receipt and creation
                flag.
        """
        cls._validate_targets(invoice=invoice)
        cls._validate_amount(amount=amount)
        cls._validate_invoice_paid(invoice=invoice)

        existing_receipt = cls._get_existing_receipt_for_invoice(
            invoice=invoice,
            payment_intent_reference=payment_intent_reference,
            external_reference=external_reference,
        )
        if existing_receipt is not None:
            return ReceiptIssuanceResult(
                receipt=existing_receipt,
                created=False,
            )

        receipt = ReceiptService.issue_receipt(
            website=invoice.website,
            amount=amount,
            currency=invoice.currency,
            client=invoice.client,
            recipient_email=invoice.recipient_email,
            recipient_name=invoice.recipient_name,
            invoice=invoice,
            payment_intent_reference=payment_intent_reference,
            external_reference=external_reference,
            payment_provider=cls._build_provider_snapshot(
                invoice=invoice,
                payment_provider=payment_provider,
            ),
        )

        if send_email:
            cls._send_receipt_email(
                receipt=receipt,
                triggered_by=triggered_by,
            )

        return ReceiptIssuanceResult(receipt=receipt, created=True)

    @classmethod
    @transaction.atomic
    def issue_receipt_for_payment_request(
        cls,
        *,
        payment_request: PaymentRequest,
        amount: Decimal,
        payment_intent_reference: str = "",
        external_reference: str = "",
        payment_provider: str = "",
        send_email: bool = True,
        triggered_by=None,
    ) -> ReceiptIssuanceResult:
        """
        Issue a receipt for a fully paid billing payment request.

        Args:
            payment_request:
                Fully paid billing payment request.
            amount:
                Settled amount acknowledged by the receipt.
            payment_intent_reference:
                Payment intent reference for settlement.
            external_reference:
                External provider reference for settlement.
            payment_provider:
                Provider used for settlement.
            send_email:
                Whether to emit receipt notification email.
            triggered_by:
                Optional actor associated with issuance.

        Returns:
            ReceiptIssuanceResult:
                Structured result containing the receipt and creation
                flag.
        """
        cls._validate_targets(payment_request=payment_request)
        cls._validate_amount(amount=amount)
        cls._validate_payment_request_paid(
            payment_request=payment_request
        )

        existing_receipt = (
            cls._get_existing_receipt_for_payment_request(
                payment_request=payment_request,
                payment_intent_reference=payment_intent_reference,
                external_reference=external_reference,
            )
        )
        if existing_receipt is not None:
            return ReceiptIssuanceResult(
                receipt=existing_receipt,
                created=False,
            )

        receipt = ReceiptService.issue_receipt(
            website=payment_request.website,
            amount=amount,
            currency=payment_request.currency,
            client=payment_request.client,
            recipient_email=payment_request.recipient_email,
            recipient_name=payment_request.recipient_name,
            payment_request=payment_request,
            payment_intent_reference=payment_intent_reference,
            external_reference=external_reference,
            payment_provider=cls._build_provider_snapshot(
                payment_request=payment_request,
                payment_provider=payment_provider,
            ),
        )

        if send_email:
            cls._send_receipt_email(
                receipt=receipt,
                triggered_by=triggered_by,
            )

        return ReceiptIssuanceResult(receipt=receipt, created=True)