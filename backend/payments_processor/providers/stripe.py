from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.conf import settings

from payments_processor.providers.base import (
    BasePaymentProvider,
    ProviderCheckoutResult,
    ProviderPaymentVerificationResult,
    ProviderRefundRequest,
    ProviderRefundResult,
    ProviderPaymentRequest,
    ProviderVerificationRequest,
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

_SUCCESS_EVENTS = {
    "checkout.session.completed",
    "payment_intent.succeeded",
}
_FAILED_EVENTS = {
    "payment_intent.payment_failed",
    "charge.failed",
    "checkout.session.expired",
}


def _stripe():
    import stripe as _s  # noqa: PLC0415
    _s.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")
    return _s


def _to_cents(amount: Decimal) -> int:
    return int((amount * 100).to_integral_value())


def _from_cents(amount_cents: int | None, currency: str = "USD") -> Decimal:
    if amount_cents is None:
        return Decimal("0.00")
    zero_decimal = {
        "JPY", "KRW", "VND", "CLP", "GNF", "ISK", "MGA",
        "PYG", "RWF", "UGX", "XAF", "XOF",
    }
    if currency.upper() in zero_decimal:
        return Decimal(str(amount_cents))
    return Decimal(str(amount_cents)) / Decimal("100")


class StripePaymentProvider(BasePaymentProvider):
    """
    Stripe payment provider — Checkout Sessions API.

    Receives immutable ProviderPaymentRequest / ProviderRefundRequest /
    ProviderVerificationRequest DTOs. Never accesses domain model objects.

    Settings required:
        STRIPE_SECRET_KEY          sk_live_... or sk_test_...
        STRIPE_WEBHOOK_SECRET      whsec_... (webhook verification)
        INFOQ_PAYMENT_BASE_URL     https://pay.infoq.com
    """

    provider_name = "stripe"

    # ------------------------------------------------------------------
    # create_payment
    # ------------------------------------------------------------------

    def create_payment(
        self,
        request: ProviderPaymentRequest,
    ) -> ProviderCheckoutResult:
        stripe = _stripe()

        try:
            session = stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": request.currency.lower(),
                            "unit_amount": _to_cents(request.amount),
                            "product_data": {
                                "name": request.product_name,
                            },
                        },
                        "quantity": 1,
                    }
                ],
                client_reference_id=request.merchant_reference,
                customer_email=request.customer_email or None,
                metadata=request.metadata.to_dict(),
                success_url=request.success_url,
                cancel_url=request.cancel_url,
            )
        except stripe.error.StripeError as exc:
            log.exception(
                "Stripe checkout.Session.create failed ref=%s: %s",
                request.merchant_reference,
                exc,
            )
            return ProviderCheckoutResult(
                success=False,
                provider_name=self.provider_name,
                provider_reference=request.merchant_reference,
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
        stripe = _stripe()
        webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

        if not webhook_secret:
            log.error(
                "STRIPE_WEBHOOK_SECRET not configured — rejecting webhook."
            )
            return ProviderWebhookVerificationResult(
                is_verified=False,
                error_message="Webhook secret not configured on this server.",
            )

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
        if not payload:
            raise PaymentProviderWebhookError("Webhook payload is empty.")

        event_type: str = str(payload.get("type", ""))
        event_id: str = str(payload.get("id", ""))
        data_object: dict = payload.get("data", {}).get("object", {})

        reference = (
            data_object.get("client_reference_id")
            or (data_object.get("metadata") or {}).get("merchant_reference")
            or (data_object.get("metadata") or {}).get("reference")
            or ""
        )

        if event_type.startswith("checkout.session"):
            provider_transaction_id = (
                data_object.get("payment_intent") or data_object.get("id", "")
            )
        else:
            provider_transaction_id = data_object.get("id", "")

        raw_currency = str(data_object.get("currency", "USD")).upper()
        amount_cents = (
            data_object.get("amount_total") or data_object.get("amount")
        )
        amount = _from_cents(amount_cents, raw_currency) if amount_cents is not None else None

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
        request: ProviderRefundRequest,
    ) -> ProviderRefundResult:
        stripe = _stripe()

        if request.amount <= Decimal("0.00"):
            raise PaymentProviderRefundError("Refund amount must be positive.")

        # Prefer the checkout session ID; fall back to the payment intent ID.
        lookup_id = request.provider_checkout_id or request.provider_payment_id

        if not lookup_id:
            raise PaymentProviderRefundError(
                f"No provider reference available for refund "
                f"'{request.merchant_reference}'."
            )

        try:
            if lookup_id.startswith("cs_"):
                session = stripe.checkout.Session.retrieve(lookup_id)
                pi_id = session.payment_intent
            elif lookup_id.startswith("pi_"):
                pi_id = lookup_id
            else:
                pi_id = lookup_id

            pi = stripe.PaymentIntent.retrieve(pi_id)
            charge_id = pi.latest_charge

            refund = stripe.Refund.create(
                charge=charge_id,
                amount=_to_cents(request.amount),
            )
        except stripe.error.StripeError as exc:
            log.exception(
                "Stripe refund failed ref=%s: %s",
                request.merchant_reference,
                exc,
            )
            raise PaymentProviderRefundError(str(exc)) from exc

        return ProviderRefundResult(
            success=True,
            status=refund.status or "succeeded",
            amount=request.amount,
            currency=request.currency.upper(),
            provider_name=self.provider_name,
            provider_refund_id=refund.id,
            provider_transaction_id=str(charge_id or ""),
            reference=request.merchant_reference,
            raw_response={"refund_id": refund.id, "status": refund.status},
        )

    # ------------------------------------------------------------------
    # verify_payment
    # ------------------------------------------------------------------

    def verify_payment(
        self,
        request: ProviderVerificationRequest,
    ) -> ProviderPaymentVerificationResult:
        stripe = _stripe()

        lookup_id = request.provider_checkout_id or request.provider_payment_id

        if not lookup_id:
            raise PaymentProviderVerificationError(
                f"No provider reference for '{request.merchant_reference}'."
            )

        try:
            if lookup_id.startswith("cs_"):
                obj = stripe.checkout.Session.retrieve(lookup_id)
                payment_status = obj.payment_status
                amount_total = obj.amount_total
                raw_currency = str(obj.currency or "USD").upper()
                pi_id = obj.payment_intent or ""
                status = "success" if payment_status == "paid" else "pending"
            else:
                obj = stripe.PaymentIntent.retrieve(lookup_id)
                pi_id = obj.id
                amount_total = obj.amount
                raw_currency = str(obj.currency or "USD").upper()
                stripe_status = obj.status
                status = (
                    "success" if stripe_status == "succeeded"
                    else "failed" if stripe_status in ("canceled", "requires_payment_method")
                    else "pending"
                )
        except stripe.error.StripeError as exc:
            log.exception(
                "Stripe verify_payment failed ref=%s: %s",
                request.merchant_reference,
                exc,
            )
            raise PaymentProviderVerificationError(str(exc)) from exc

        return ProviderPaymentVerificationResult(
            success=True,
            status=status,
            amount=_from_cents(amount_total, raw_currency),
            currency=raw_currency,
            provider_name=self.provider_name,
            provider_reference=lookup_id,
            provider_transaction_id=str(pi_id),
            provider_event_id="",
            reference=request.merchant_reference,
            raw_response={"provider_reference": lookup_id, "status": status},
        )


register_provider(StripePaymentProvider)
