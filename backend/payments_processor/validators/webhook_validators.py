from __future__ import annotations

from typing import Any

from payments_processor.enums import PaymentProvider
from payments_processor.exceptions import PaymentError


def validate_webhook_provider(provider: str) -> None:
    """
    Ensure webhook provider is supported.

    Args:
        provider: Provider name.

    Raises:
        PaymentError: If provider is invalid.
    """
    if provider not in PaymentProvider.values:
        raise PaymentError(f"Unsupported webhook provider '{provider}'.")
    


def validate_webhook_payload(payload: dict[str, Any] | None) -> None:
    """
    Ensure webhook payload is present and valid.

    Args:
        payload: Raw webhook payload.

    Raises:
        PaymentError: If payload is invalid.
    """
    if payload is None:
        raise PaymentError("Webhook payload is missing.")

    if not isinstance(payload, dict):
        raise PaymentError("Webhook payload must be a dictionary.")

    if not payload:
        raise PaymentError("Webhook payload is empty.")
    

def validate_webhook_event_id(event_id: str | None) -> None:
    """
    Ensure webhook event ID exists.

    Args:
        event_id: Provider event ID.

    Raises:
        PaymentError: If missing.
    """
    if not event_id:
        raise PaymentError("Webhook event ID is required.")
    

def validate_webhook_event_type(event_type: str | None) -> None:
    """
    Ensure webhook event type exists.

    Args:
        event_type: Provider event type.

    Raises:
        PaymentError: If missing.
    """
    if not event_type:
        raise PaymentError("Webhook event type is required.")
    

def validate_webhook_not_processed(
    *,
    existing_event,
) -> None:
    """
    Ensure webhook event has not already been processed.

    Args:
        existing_event: Existing webhook event instance.

    Raises:
        PaymentError: If already processed.
    """
    if existing_event is None:
        return

    if existing_event.processing_status == "processed":
        raise PaymentError("Webhook event already processed.")
    


def validate_webhook_payment_intent(
    payment_intent,
) -> None:
    """
    Ensure webhook maps to a known payment intent.

    Args:
        payment_intent: PaymentIntent instance.

    Raises:
        PaymentError: If missing.
    """
    if payment_intent is None:
        raise PaymentError(
            "Webhook could not be mapped to a payment intent."
        )
    


def validate_signature_verified(is_verified: bool) -> None:
    """
    Ensure webhook signature has been verified.

    Args:
        is_verified: Result of provider signature validation.

    Raises:
        PaymentError: If not verified.
    """
    if not is_verified:
        raise PaymentError("Webhook signature verification failed.")
    


def validate_webhook_status_transition(
    *,
    current_status: str,
    new_status: str,
) -> None:
    """
    Prevent invalid or regressive status transitions.

    Args:
        current_status: Existing payment status.
        new_status: Incoming status from webhook.

    Raises:
        PaymentError: If transition is invalid.
    """
    if current_status == "succeeded":
        raise PaymentError(
            "Cannot override a succeeded payment intent."
        )

    if current_status == "refunded":
        raise PaymentError(
            "Cannot modify a refunded payment intent."
        )