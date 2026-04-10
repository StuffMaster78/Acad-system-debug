from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class ProviderCheckoutResult:
    """
    Result returned when initializing a payment with a provider.
    """

    provider_name: str
    provider_reference: str
    checkout_url: str | None = None
    payment_url: str | None = None
    access_code: str | None = None
    client_secret: str | None = None
    expires_at: Any | None = None
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderWebhookVerificationResult:
    """
    Result of webhook signature / authenticity verification.
    """

    is_valid: bool
    error_message: str = ""


@dataclass(slots=True)
class ProviderWebhookEvent:
    """
    Normalized provider webhook event payload.
    """

    event_id: str
    event_type: str
    status: str
    amount: Decimal
    currency: str
    provider_transaction_id: str
    provider_reference: str
    raw_payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderRefundResult:
    """
    Result returned when a refund is initiated or confirmed.
    """

    provider_name: str
    provider_reference: str
    refund_reference: str
    status: str
    amount: Decimal
    currency: str
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderPaymentVerificationResult:
    """
    Result returned when verifying a payment directly with the provider.
    Useful for reconciliation jobs.
    """

    provider_name: str
    provider_reference: str
    provider_transaction_id: str
    status: str
    amount: Decimal
    currency: str
    raw_response: dict[str, Any] = field(default_factory=dict)


class BasePaymentProvider(ABC):
    """
    Base contract for all payment providers.

    Every provider should normalize its outputs into the internal
    provider result objects defined above.
    """

    provider_name: str

    @abstractmethod
    def create_payment(
        self,
        payment_intent: Any,
    ) -> ProviderCheckoutResult:
        """
        Initialize a payment with the provider.

        Args:
            payment_intent: Internal payment intent domain object.

        Returns:
            ProviderCheckoutResult
        """
        raise NotImplementedError

    @abstractmethod
    def verify_webhook(
        self,
        payload: dict[str, Any],
        headers: dict[str, Any],
    ) -> ProviderWebhookVerificationResult:
        """
        Verify provider webhook authenticity or signature.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_webhook(
        self,
        payload: dict[str, Any],
    ) -> ProviderWebhookEvent:
        """
        Normalize a provider webhook payload into an internal event object.
        """
        raise NotImplementedError

    @abstractmethod
    def refund_payment(
        self,
        payment_intent: Any,
        amount: Decimal | None = None,
    ) -> ProviderRefundResult:
        """
        Execute a refund through the provider.

        Args:
            payment_intent: Internal payment intent domain object.
            amount: Optional partial refund amount. If omitted, provider
                should refund the full eligible amount.
        """
        raise NotImplementedError

    @abstractmethod
    def verify_payment(
        self,
        payment_intent: Any,
    ) -> ProviderPaymentVerificationResult:
        """
        Fetch payment status directly from provider.
        Useful for reconciliation and manual verification.
        """
        raise NotImplementedError