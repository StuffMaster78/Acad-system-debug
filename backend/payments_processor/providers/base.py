from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


# ---------------------------------------------------------------------------
# Inbound request DTOs — passed TO providers
# ---------------------------------------------------------------------------

@dataclass(slots=True, frozen=True)
class ProviderMetadata:
    """
    The complete, immutable set of fields that may be sent to any provider
    as payment metadata.

    Frozen so no caller can add business-specific keys after construction.
    Providers call .to_dict() when they need a plain dict for their API.
    """
    merchant_reference: str
    environment: str

    def to_dict(self) -> dict[str, str]:
        return {
            "merchant_reference": self.merchant_reference,
            "environment": self.environment,
        }


@dataclass(slots=True, frozen=True)
class ProviderPaymentRequest:
    """
    Everything a provider needs to initialise a checkout session.

    Only InfoQ-controlled, semantically neutral fields are present.
    Domain objects (order, invoice, website, payable) are never included.
    The assembler is the only place that reads the domain model and populates
    this DTO.
    """
    merchant_reference: str
    amount: Decimal
    currency: str
    product_name: str
    success_url: str
    cancel_url: str
    customer_email: str
    metadata: ProviderMetadata = field(default_factory=lambda: ProviderMetadata(merchant_reference="", environment=""))


@dataclass(slots=True, frozen=True)
class ProviderRefundRequest:
    """
    Everything a provider needs to execute a refund.

    provider_checkout_id holds the provider checkout/session reference
    (e.g. Stripe cs_xxx). provider_payment_id holds the underlying payment
    object ID (e.g. Stripe pi_xxx), populated after the first webhook.
    Providers use whichever identifier they need.
    """
    merchant_reference: str
    amount: Decimal
    currency: str
    provider_checkout_id: str = ""
    provider_payment_id: str = ""


@dataclass(slots=True, frozen=True)
class ProviderVerificationRequest:
    """
    Everything a provider needs to poll payment status.
    """
    merchant_reference: str
    provider_checkout_id: str = ""
    provider_payment_id: str = ""


# ---------------------------------------------------------------------------
# Outbound result DTOs — returned FROM providers
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class ProviderCheckoutResult:
    """
    Result returned when initializing a payment with a provider.
    """
    success: bool
    provider_name: str
    provider_reference: str
    checkout_url: str | None = None
    payment_url: str | None = None
    status: str = ""
    access_code: str | None = None
    client_secret: str | None = None
    expires_at: Any | None = None
    raw_response: dict[str, Any] = field(default_factory=dict)
    error_message: str = ""


@dataclass(slots=True)
class ProviderWebhookVerificationResult:
    """
    Result of webhook signature / authenticity verification.
    """
    is_verified: bool
    error_message: str = ""
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderWebhookEvent:
    """
    Normalized provider webhook event payload.
    """
    event_id: str
    event_type: str
    status: str
    reference: str
    amount: Decimal | None = None
    currency: str = ""
    provider_transaction_id: str = ""
    provider_event_id: str = ""
    raw_payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderRefundResult:
    """
    Result returned when a refund is initiated or confirmed.
    """
    success: bool
    status: str
    amount: Decimal
    currency: str
    provider_name: str
    provider_refund_id: str = ""
    provider_transaction_id: str = ""
    reference: str = ""
    raw_response: dict[str, Any] = field(default_factory=dict)
    error_message: str = ""


@dataclass(slots=True)
class ProviderPaymentVerificationResult:
    """
    Result returned when verifying a payment directly with the provider.
    Useful for reconciliation jobs.
    """
    success: bool
    status: str
    amount: Decimal
    currency: str
    provider_name: str
    provider_reference: str
    provider_transaction_id: str
    provider_event_id: str = ""
    reference: str = ""
    raw_response: dict[str, Any] = field(default_factory=dict)
    error_message: str = ""


# ---------------------------------------------------------------------------
# Base provider contract
# ---------------------------------------------------------------------------

class BasePaymentProvider(ABC):
    """
    Base contract for all payment providers.

    Providers receive immutable request DTOs and return result DTOs.
    They never receive domain model instances — the ProviderRequestAssembler
    is the only translation layer between the domain and this interface.
    """

    provider_name: str

    @abstractmethod
    def create_payment(
        self,
        request: ProviderPaymentRequest,
    ) -> ProviderCheckoutResult:
        """Initialize a checkout session with the provider."""
        raise NotImplementedError

    @abstractmethod
    def verify_webhook(
        self,
        payload: dict[str, Any],
        headers: dict[str, Any],
    ) -> ProviderWebhookVerificationResult:
        """Verify provider webhook authenticity or signature."""
        raise NotImplementedError

    @abstractmethod
    def parse_webhook(
        self,
        payload: dict[str, Any],
    ) -> ProviderWebhookEvent:
        """Normalize a provider webhook payload into an internal event."""
        raise NotImplementedError

    @abstractmethod
    def refund_payment(
        self,
        request: ProviderRefundRequest,
    ) -> ProviderRefundResult:
        """Execute a refund through the provider."""
        raise NotImplementedError

    @abstractmethod
    def verify_payment(
        self,
        request: ProviderVerificationRequest,
    ) -> ProviderPaymentVerificationResult:
        """Fetch payment status directly from the provider."""
        raise NotImplementedError
