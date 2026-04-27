from __future__ import annotations

from dataclasses import dataclass

from django.core.exceptions import ValidationError

from billing.constants import InvoiceStatus, PaymentRequestStatus
from billing.models.invoice import Invoice
from billing.models.payment_request import PaymentRequest
from billing.selectors.invoice_selectors import InvoiceSelector
from billing.selectors.payment_request_selectors import (
    PaymentRequestSelector,
)
from billing.services.invoice_orchestration_service import (
    InvoiceOrchestrationService,
)
from billing.services.payment_request_orchestration_service import (
    PaymentRequestOrchestrationService,
)
from billing.services.invoice_orchestration_service import (
    InvoiceIntentPreparationResult,
    InvoiceOrchestrationService,
)
from billing.services.payment_request_orchestration_service import (
    PaymentRequestIntentPreparationResult,
    PaymentRequestOrchestrationService,
)

@dataclass(frozen=True)
class InvoicePaymentAccessResult:
    """
    Represent the outcome of resolving and preparing invoice payment
    access from a secure token.

    Attributes:
        invoice:
            Invoice resolved by token.
        preparation_result:
            Result returned by InvoiceOrchestrationService.
    """

    invoice: Invoice
    preparation_result: InvoiceIntentPreparationResult


@dataclass(frozen=True)
class PaymentRequestAccessResult:
    """
    Represent the outcome of resolving and preparing payment request
    access from a secure token.

    Attributes:
        payment_request:
            Billing payment request resolved by token.
        preparation_result:
            Result returned by PaymentRequestOrchestrationService.
    """

    payment_request: PaymentRequest
    preparation_result: PaymentRequestIntentPreparationResult


class PaymentAccessService:
    """
    Coordinate public token-based access to billing payment flows.

    This service resolves invoices and payment requests by secure token,
    validates their payable state, and delegates checkout preparation to
    the existing billing orchestration services.
    """

    @staticmethod
    def _validate_invoice_access(*, invoice: Invoice) -> None:
        """
        Validate that an invoice is payable through token access.

        Args:
            invoice:
                Invoice resolved by token.

        Raises:
            ValidationError:
                Raised when invoice is terminal or token is invalid.
        """
        if invoice.status in {
            InvoiceStatus.PAID,
            InvoiceStatus.CANCELLED,
            InvoiceStatus.EXPIRED,
        }:
            raise ValidationError(
                "This invoice is no longer payable."
            )

        if not InvoiceSelector.is_token_valid(invoice=invoice):
            raise ValidationError(
                "This invoice payment link is invalid or expired."
            )

    @staticmethod
    def _validate_payment_request_access(
        *,
        payment_request: PaymentRequest,
    ) -> None:
        """
        Validate that a payment request is payable through token access.

        Args:
            payment_request:
                Billing payment request resolved by token.

        Raises:
            ValidationError:
                Raised when payment request is terminal or token is
                invalid.
        """
        if payment_request.status in {
            PaymentRequestStatus.PAID,
            PaymentRequestStatus.CANCELLED,
            PaymentRequestStatus.EXPIRED,
        }:
            raise ValidationError(
                "This payment request is no longer payable."
            )

        if not PaymentRequestSelector.is_token_valid(
            payment_request=payment_request
        ):
            raise ValidationError(
                "This payment request link is invalid or expired."
            )

    @classmethod
    def resolve_invoice_by_token(cls, *, token: str) -> Invoice:
        """
        Resolve an invoice by payment token and validate access.

        Args:
            token:
                Secure invoice payment token.

        Returns:
            Invoice:
                Resolved payable invoice.

        Raises:
            ValidationError:
                Raised when token is invalid or invoice is not payable.
        """
        try:
            invoice = Invoice.objects.get(payment_token=token)
        except Invoice.DoesNotExist as exc:
            raise ValidationError(
                "Invalid invoice payment link."
            ) from exc

        cls._validate_invoice_access(invoice=invoice)
        return invoice

    @classmethod
    def resolve_payment_request_by_token(
        cls,
        *,
        token: str,
    ) -> PaymentRequest:
        """
        Resolve a payment request by token and validate access.

        Args:
            token:
                Secure payment request token.

        Returns:
            PaymentRequest:
                Resolved payable billing payment request.

        Raises:
            ValidationError:
                Raised when token is invalid or request is not payable.
        """
        try:
            payment_request = PaymentRequest.objects.get(
                payment_token=token
            )
        except PaymentRequest.DoesNotExist as exc:
            raise ValidationError(
                "Invalid payment request link."
            ) from exc

        cls._validate_payment_request_access(
            payment_request=payment_request
        )
        return payment_request

    @classmethod
    def prepare_invoice_payment_by_token(
        cls,
        *,
        token: str,
        provider: str,
    ) -> InvoicePaymentAccessResult:
        """
        Resolve and prepare invoice payment access from a secure token.

        Args:
            token:
                Secure invoice payment token.
            provider:
                Provider key used to initialize checkout.

        Returns:
            InvoicePaymentAccessResult:
                Resolved invoice and preparation result.
        """
        invoice = cls.resolve_invoice_by_token(token=token)

        preparation_result = (
            InvoiceOrchestrationService.issue_invoice_and_prepare_payment(
                invoice=invoice,
                provider=provider,
                generate_token=False,
                send_notification=False,
                triggered_by=None,
            )
        )

        return InvoicePaymentAccessResult(
            invoice=invoice,
            preparation_result=preparation_result,
        )

    @classmethod
    def prepare_payment_request_payment_by_token(
        cls,
        *,
        token: str,
        provider: str,
    ) -> PaymentRequestAccessResult:
        """
        Resolve and prepare payment request payment access from a secure
        token.

        Args:
            token:
                Secure payment request token.
            provider:
                Provider key used to initialize checkout.

        Returns:
            PaymentRequestAccessResult:
                Resolved payment request and preparation result.
        """
        payment_request = cls.resolve_payment_request_by_token(
            token=token
        )

        preparation_result = (
            PaymentRequestOrchestrationService
            .issue_payment_request_and_prepare_payment(
                payment_request=payment_request,
                provider=provider,
                generate_token=False,
                send_notification=False,
                triggered_by=None,
            )
        )

        return PaymentRequestAccessResult(
            payment_request=payment_request,
            preparation_result=preparation_result,
        )