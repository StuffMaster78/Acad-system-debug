from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.conf import settings

from payments_processor.providers.base import (
    BasePaymentProvider,
    ProviderCheckoutResult,
    ProviderPaymentVerificationResult,
    ProviderRefundResult,
    ProviderWebhookEvent,
    ProviderWebhookVerificationResult,
)
from payments_processor.providers.exceptions import (
    PaymentProviderRefundError,
    PaymentProviderVerificationError,
    PaymentProviderWebhookError,
)
from payments_processor.providers.registry import register_provider

log = logging.getLogger(__name__)

# Stripe event types that represent a successful payment.
_SUCCESS_EVENTS = {
    "checkout.session.completed",
    "payment_intent.succeeded",
}
# Stripe event types that represent a failed payment.
_FAILED_EVENTS = {
    "payment_intent.payment_failed",
    "charge.failed",
    "checkout.session.expired",
}


def _stripe():
    """
    Lazily import and configure stripe.

    Reads STRIPE_SECRET_KEY from Django settings at call time so the
    setting can be overridden in tests without patching the module.
    """
    import stripe as _s

    _s.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")
    return _s


def _to_cents(amount: Decimal) -> int:
    """Convert a Decimal amount to Stripe's integer cent format."""
    return int((amount * 100).to_integral_value())


def _from_cents(amount_cents: int | None, currency: str = "USD") -> Decimal:
    """Convert Stripe cent integer back to Decimal."""
    if amount_cents is None:
        return Decimal("0.00")
    # JPY and other zero-decimal currencies use the amount directly.
    zero_decimal = {"JPY", "KRW", "VND", "CLP", "GNF", "ISK", "MGA", "PYG", "RWF", "UGX", "XAF", "XOF"}
    if currency.upper() in zero_decimal:
        return Decimal(str(amount_cents))
    return Decimal(str(amount_cents)) / Decimal("100")


class StripePaymentProvider(BasePaymentProvider):
    """
    Stripe payment provider — Checkout Sessions API.

    Flow:
        create_payment  → stripe.checkout.Session.create()
                          Returns a hosted payment URL.
                          Session ID stored as provider_reference.

        verify_webhook  → stripe.Webhook.construct_event()
                          Uses raw body bytes + Stripe-Signature header.
                          Raw bytes passed via headers["_raw_body"].

        parse_webhook   → Normalises the Stripe event into ProviderWebhookEvent.

        refund_payment  → stripe.Refund.create()

        verify_payment  → stripe.checkout.Session.retrieve() or
                          stripe.PaymentIntent.retrieve()

    Settings required:
        STRIPE_SECRET_KEY       sk_live_... or sk_test_...
        STRIPE_WEBHOOK_SECRET   whsec_...  (for webhook verification)
        STRIPE_PUBLISHABLE_KEY  pk_live_... or pk_test_... (returned to client)
        FRONTEND_URL            Base URL for success/cancel redirect pages
    """

    provider_name = "stripe"

    # ------------------------------------------------------------------
    # create_payment
    # ------------------------------------------------------------------

    def create_payment(
        self,
        payment_intent: Any,
    ) -> ProviderCheckoutResult:
        """
        Create a Stripe Checkout Session and return the hosted payment URL.
        """
        stripe = _stripe()

        amount = Decimal(str(getattr(payment_intent, "amount", "0.00")))
        currency = str(getattr(payment_intent, "currency", "USD")).lower()
        reference = str(getattr(payment_intent, "reference", ""))
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")

        client = getattr(payment_intent, "client", None)
        client_email = getattr(client, "email", None) if client else None

        try:
            session = stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": currency,
                            "unit_amount": _to_cents(amount),
                            "product_data": {
                                "name": f"Order payment — {reference}",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                client_reference_id=reference,
                customer_email=client_email,
                metadata={"reference": reference},
                success_url=(
                    f"{frontend_url}/client/billing"
                    f"?payment=success&ref={reference}"
                ),
                cancel_url=(
                    f"{frontend_url}/client/billing"
                    f"?payment=cancelled&ref={reference}"
                ),
            )
        except stripe.error.StripeError as exc:
            log.exception("Stripe checkout.Session.create failed ref=%s: %s", reference, exc)
            return ProviderCheckoutResult(
                success=False,
                provider_name=self.provider_name,
                provider_reference=reference,
                error_message=str(exc),
            )

        return ProviderCheckoutResult(
            success=True,
            provider_name=self.provider_name,
            provider_reference=session.id,
            checkout_url=session.url,
            client_secret=getattr(session, "client_secret", None),
            status=session.status or "open",
            raw_response={"session_id": session.id, "status": session.status},
        )

    # ------------------------------------------------------------------
    # verify_webhook
    # ------------------------------------------------------------------

    def verify_webhook(
        self,
        payload: dict[str, Any],
        headers: dict[str, Any],
    ) -> ProviderWebhookVerificationResult:
        """
        Verify the Stripe-Signature header using the webhook secret.

        Requires headers["_raw_body"] (bytes) injected by the webhook view.
        Falls back to allowing if the webhook secret is not configured (dev).
        """
        stripe = _stripe()
        webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

        if not webhook_secret:
            log.warning(
                "STRIPE_WEBHOOK_SECRET not configured — skipping signature verification."
            )
            return ProviderWebhookVerificationResult(is_verified=True)

        raw_body: bytes = headers.get("_raw_body", b"")
        sig_header: str = headers.get("HTTP_STRIPE_SIGNATURE", "")

        if not raw_body:
            return ProviderWebhookVerificationResult(
                is_verified=False,
                error_message="Raw body missing — cannot verify Stripe signature.",
            )

        if not sig_header:
            return ProviderWebhookVerificationResult(
                is_verified=False,
                error_message="Stripe-Signature header missing.",
            )

        try:
            stripe.Webhook.construct_event(raw_body, sig_header, webhook_secret)
        except stripe.error.SignatureVerificationError as exc:
            return ProviderWebhookVerificationResult(
                is_verified=False,
                error_message=str(exc),
            )
        except Exception as exc:
            log.exception("Stripe webhook verification error: %s", exc)
            return ProviderWebhookVerificationResult(
                is_verified=False,
                error_message=str(exc),
            )

        return ProviderWebhookVerificationResult(is_verified=True)

    # ------------------------------------------------------------------
    # parse_webhook
    # ------------------------------------------------------------------

    def parse_webhook(
        self,
        payload: dict[str, Any],
    ) -> ProviderWebhookEvent:
        """
        Normalise a Stripe event payload into ProviderWebhookEvent.

        Handles both checkout.session.* and payment_intent.* event shapes.
        """
        if not payload:
            raise PaymentProviderWebhookError("Webhook payload is empty.")

        event_type: str = str(payload.get("type", ""))
        event_id: str = str(payload.get("id", ""))
        data_object: dict = payload.get("data", {}).get("object", {})

        # ── Reference ──────────────────────────────────────────────────
        reference = (
            data_object.get("client_reference_id")
            or (data_object.get("metadata") or {}).get("reference")
            or ""
        )

        # ── Provider transaction ID ────────────────────────────────────
        # For checkout sessions the charge is nested; for PaymentIntents it's direct.
        if event_type.startswith("checkout.session"):
            provider_transaction_id = data_object.get("payment_intent") or data_object.get("id", "")
        else:
            provider_transaction_id = data_object.get("id", "")

        # ── Amount ─────────────────────────────────────────────────────
        raw_currency = str(data_object.get("currency", "USD")).upper()
        amount_cents = (
            data_object.get("amount_total")
            or data_object.get("amount")
        )
        amount = _from_cents(amount_cents, raw_currency) if amount_cents is not None else None

        # ── Status ─────────────────────────────────────────────────────
        if event_type in _SUCCESS_EVENTS:
            status = "success"
        elif event_type in _FAILED_EVENTS:
            status = "failed"
        else:
            status = "pending"

        return ProviderWebhookEvent(
            event_id=event_id,
            event_type=event_type,
            status=status,
            reference=str(reference),
            amount=amount,
            currency=raw_currency,
            provider_transaction_id=str(provider_transaction_id),
            provider_event_id=event_id,
            raw_payload=payload,
        )

    # ------------------------------------------------------------------
    # refund_payment
    # ------------------------------------------------------------------

    def refund_payment(
        self,
        payment_intent: Any,
        *,
        amount: Decimal | None = None,
    ) -> ProviderRefundResult:
        """
        Create a Stripe refund for a payment intent or charge.
        """
        stripe = _stripe()

        refund_amount = amount or Decimal(str(getattr(payment_intent, "amount", "0.00")))
        currency = str(getattr(payment_intent, "currency", "USD")).upper()
        reference = str(getattr(payment_intent, "reference", ""))

        if refund_amount <= Decimal("0.00"):
            raise PaymentProviderRefundError("Refund amount must be positive.")

        # provider_reference is the Stripe session/PaymentIntent ID.
        provider_reference = str(getattr(payment_intent, "provider_reference", ""))

        # Retrieve the charge ID from the PaymentIntent so we can refund it.
        try:
            if provider_reference.startswith("cs_"):
                # Checkout session — retrieve to get payment_intent
                session = stripe.checkout.Session.retrieve(provider_reference)
                pi_id = session.payment_intent
            else:
                pi_id = provider_reference

            pi = stripe.PaymentIntent.retrieve(pi_id)
            charge_id = pi.latest_charge

            refund = stripe.Refund.create(
                charge=charge_id,
                amount=_to_cents(refund_amount),
            )
        except stripe.error.StripeError as exc:
            log.exception("Stripe refund failed ref=%s: %s", reference, exc)
            raise PaymentProviderRefundError(str(exc)) from exc

        return ProviderRefundResult(
            success=True,
            status=refund.status or "succeeded",
            amount=refund_amount,
            currency=currency,
            provider_name=self.provider_name,
            provider_refund_id=refund.id,
            provider_transaction_id=str(charge_id or ""),
            reference=reference,
            raw_response={"refund_id": refund.id, "status": refund.status},
        )

    # ------------------------------------------------------------------
    # verify_payment
    # ------------------------------------------------------------------

    def verify_payment(
        self,
        payment_intent: Any,
    ) -> ProviderPaymentVerificationResult:
        """
        Retrieve the current payment status directly from Stripe.
        """
        stripe = _stripe()

        provider_reference = str(getattr(payment_intent, "provider_reference", ""))
        reference = str(getattr(payment_intent, "reference", ""))
        currency = str(getattr(payment_intent, "currency", "USD")).upper()

        if not provider_reference:
            raise PaymentProviderVerificationError(
                "Payment intent has no provider reference."
            )

        try:
            if provider_reference.startswith("cs_"):
                obj = stripe.checkout.Session.retrieve(provider_reference)
                payment_status = obj.payment_status  # "paid" | "unpaid" | "no_payment_required"
                amount_total = obj.amount_total
                pi_id = obj.payment_intent or ""
                status = "success" if payment_status == "paid" else "pending"
            else:
                obj = stripe.PaymentIntent.retrieve(provider_reference)
                pi_id = obj.id
                amount_total = obj.amount
                stripe_status = obj.status  # "succeeded" | "canceled" | "processing" etc.
                status = "success" if stripe_status == "succeeded" else (
                    "failed" if stripe_status in ("canceled", "requires_payment_method") else "pending"
                )
        except stripe.error.StripeError as exc:
            log.exception("Stripe verify_payment failed ref=%s: %s", reference, exc)
            raise PaymentProviderVerificationError(str(exc)) from exc

        amount = _from_cents(amount_total, currency)

        return ProviderPaymentVerificationResult(
            success=True,
            status=status,
            amount=amount,
            currency=currency,
            provider_name=self.provider_name,
            provider_reference=provider_reference,
            provider_transaction_id=str(pi_id),
            provider_event_id="",
            reference=reference,
            raw_response={
                "provider_reference": provider_reference,
                "status": status,
            },
        )


register_provider(StripePaymentProvider)
