"""
Provider contract tests.

Every provider registered in the system must satisfy this contract.
These tests run against the Mock provider directly and serve as the
template that Stripe, PayPal, Flutterwave, and any future provider
must also pass (with appropriate mocking of their HTTP clients).

Adding a new provider is mechanical once these tests pass.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from payments_processor.providers.base import (
    ProviderCheckoutResult,
    ProviderMetadata,
    ProviderPaymentRequest,
    ProviderPaymentVerificationResult,
    ProviderRefundRequest,
    ProviderRefundResult,
    ProviderVerificationRequest,
    ProviderWebhookEvent,
    ProviderWebhookVerificationResult,
)
from payments_processor.providers.mock import MockPaymentProvider
from payments_processor.providers.registry import get_provider


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _payment_request(
    *,
    reference: str = "INFQ_contract_test",
    amount: Decimal = Decimal("50.00"),
    currency: str = "USD",
) -> ProviderPaymentRequest:
    return ProviderPaymentRequest(
        merchant_reference=reference,
        amount=amount,
        currency=currency,
        product_name="InfoQ Digital Service",
        success_url="https://pay.infoq.com/payment/complete?status=success&ref=" + reference,
        cancel_url="https://pay.infoq.com/payment/complete?status=cancelled&ref=" + reference,
        customer_email="client@example.com",
        metadata=ProviderMetadata(
            merchant_reference=reference,
            environment="test",
        ),
    )


def _refund_request(
    *,
    reference: str = "INFQ_contract_test",
    amount: Decimal = Decimal("25.00"),
    checkout_id: str = "mock_cs_test",
    payment_id: str = "mock_pi_test",
) -> ProviderRefundRequest:
    return ProviderRefundRequest(
        merchant_reference=reference,
        amount=amount,
        currency="USD",
        provider_checkout_id=checkout_id,
        provider_payment_id=payment_id,
    )


def _verification_request(
    *,
    reference: str = "INFQ_contract_test",
    checkout_id: str = "mock_cs_test",
    payment_id: str = "mock_pi_test",
) -> ProviderVerificationRequest:
    return ProviderVerificationRequest(
        merchant_reference=reference,
        provider_checkout_id=checkout_id,
        provider_payment_id=payment_id,
    )


# ---------------------------------------------------------------------------
# Contract: every provider must satisfy these
# ---------------------------------------------------------------------------

def _assert_checkout_result_contract(result: Any) -> None:
    assert isinstance(result, ProviderCheckoutResult)
    assert isinstance(result.success, bool)
    assert isinstance(result.provider_name, str)
    assert isinstance(result.provider_reference, str)
    assert isinstance(result.raw_response, dict)


def _assert_refund_result_contract(result: Any) -> None:
    assert isinstance(result, ProviderRefundResult)
    assert isinstance(result.success, bool)
    assert isinstance(result.status, str)
    assert isinstance(result.amount, Decimal)
    assert isinstance(result.currency, str)
    assert isinstance(result.provider_name, str)
    assert isinstance(result.raw_response, dict)


def _assert_verification_result_contract(result: Any) -> None:
    assert isinstance(result, ProviderPaymentVerificationResult)
    assert isinstance(result.success, bool)
    assert isinstance(result.status, str)
    assert isinstance(result.amount, Decimal)
    assert isinstance(result.currency, str)
    assert isinstance(result.provider_name, str)
    assert isinstance(result.raw_response, dict)


def _assert_webhook_verification_contract(result: Any) -> None:
    assert isinstance(result, ProviderWebhookVerificationResult)
    assert isinstance(result.is_verified, bool)


def _assert_webhook_event_contract(result: Any) -> None:
    assert isinstance(result, ProviderWebhookEvent)
    assert isinstance(result.event_id, str)
    assert isinstance(result.event_type, str)
    assert isinstance(result.status, str)
    assert isinstance(result.reference, str)


# ---------------------------------------------------------------------------
# Mock provider — runs without network
# ---------------------------------------------------------------------------

class TestMockProviderContract:

    def setup_method(self):
        self.provider = MockPaymentProvider()

    def test_provider_name_is_string(self):
        assert isinstance(self.provider.provider_name, str)
        assert self.provider.provider_name

    def test_create_payment_satisfies_contract(self):
        result = self.provider.create_payment(_payment_request())
        _assert_checkout_result_contract(result)

    def test_create_payment_succeeds(self):
        result = self.provider.create_payment(_payment_request())
        assert result.success is True

    def test_create_payment_provider_reference_is_non_empty(self):
        result = self.provider.create_payment(_payment_request())
        assert result.provider_reference

    def test_refund_payment_satisfies_contract(self):
        result = self.provider.refund_payment(_refund_request())
        _assert_refund_result_contract(result)

    def test_refund_payment_amount_matches_request(self):
        result = self.provider.refund_payment(_refund_request(amount=Decimal("30.00")))
        assert result.amount == Decimal("30.00")

    def test_verify_payment_satisfies_contract(self):
        result = self.provider.verify_payment(_verification_request())
        _assert_verification_result_contract(result)

    def test_verify_webhook_satisfies_contract(self):
        result = self.provider.verify_webhook({}, {})
        _assert_webhook_verification_contract(result)

    def test_verify_webhook_returns_verified(self):
        result = self.provider.verify_webhook({}, {})
        assert result.is_verified is True

    def test_parse_webhook_satisfies_contract(self):
        payload = {
            "event_id": "evt_mock_001",
            "event_type": "payment.updated",
            "status": "success",
            "reference": "INFQ_mock_ref",
            "amount": "50.00",
            "currency": "USD",
        }
        result = self.provider.parse_webhook(payload)
        _assert_webhook_event_contract(result)

    def test_parse_webhook_reference_matches_payload(self):
        payload = {
            "event_id": "evt_001",
            "event_type": "payment.updated",
            "status": "success",
            "reference": "INFQ_ref_abc",
            "amount": "50.00",
            "currency": "USD",
        }
        result = self.provider.parse_webhook(payload)
        assert result.reference == "INFQ_ref_abc"


# ---------------------------------------------------------------------------
# Stripe provider — network calls mocked
# ---------------------------------------------------------------------------

class TestStripeProviderContract:

    def setup_method(self):
        self.provider = get_provider("stripe")

    def _mock_session(self, *, session_id="cs_test_abc", status="open", url="https://checkout.stripe.com/test"):
        session = MagicMock()
        session.id = session_id
        session.url = url
        session.status = status
        session.client_secret = None
        return session

    def _mock_refund(self, *, refund_id="re_test_abc", status="succeeded"):
        refund = MagicMock()
        refund.id = refund_id
        refund.status = status
        return refund

    def _mock_payment_intent(self, *, pi_id="pi_test_abc", latest_charge="ch_test_abc"):
        pi = MagicMock()
        pi.id = pi_id
        pi.latest_charge = latest_charge
        pi.amount = 5000
        pi.currency = "usd"
        pi.status = "succeeded"
        return pi

    @patch("payments_processor.providers.stripe._stripe")
    def test_create_payment_satisfies_contract(self, mock_stripe_fn):
        stripe = MagicMock()
        stripe.checkout.Session.create.return_value = self._mock_session()
        mock_stripe_fn.return_value = stripe

        result = self.provider.create_payment(_payment_request())
        _assert_checkout_result_contract(result)

    @patch("payments_processor.providers.stripe._stripe")
    def test_create_payment_returns_session_id_as_reference(self, mock_stripe_fn):
        stripe = MagicMock()
        stripe.checkout.Session.create.return_value = self._mock_session(session_id="cs_test_xyz")
        mock_stripe_fn.return_value = stripe

        result = self.provider.create_payment(_payment_request())
        assert result.provider_reference == "cs_test_xyz"

    @patch("payments_processor.providers.stripe._stripe")
    def test_create_payment_sends_relay_url_not_merchant_domain(self, mock_stripe_fn):
        stripe = MagicMock()
        stripe.checkout.Session.create.return_value = self._mock_session()
        mock_stripe_fn.return_value = stripe

        req = _payment_request()
        self.provider.create_payment(req)

        call_kwargs = stripe.checkout.Session.create.call_args.kwargs
        assert "pay.infoq.com" in call_kwargs["success_url"]
        assert "pay.infoq.com" in call_kwargs["cancel_url"]

    @patch("payments_processor.providers.stripe._stripe")
    def test_create_payment_sends_no_business_metadata(self, mock_stripe_fn):
        stripe = MagicMock()
        stripe.checkout.Session.create.return_value = self._mock_session()
        mock_stripe_fn.return_value = stripe

        self.provider.create_payment(_payment_request())

        call_kwargs = stripe.checkout.Session.create.call_args.kwargs
        sent_metadata = call_kwargs["metadata"]
        assert set(sent_metadata.keys()) == {"merchant_reference", "environment"}
        for forbidden in ("service_family", "service_code", "order_id", "invoice_title", "website"):
            assert forbidden not in sent_metadata

    @patch("payments_processor.providers.stripe._stripe")
    def test_create_payment_sends_infoq_product_name(self, mock_stripe_fn):
        stripe = MagicMock()
        stripe.checkout.Session.create.return_value = self._mock_session()
        mock_stripe_fn.return_value = stripe

        req = _payment_request()
        self.provider.create_payment(req)

        call_kwargs = stripe.checkout.Session.create.call_args.kwargs
        line_item_name = call_kwargs["line_items"][0]["price_data"]["product_data"]["name"]
        assert line_item_name.startswith("InfoQ")
        for forbidden in ("order", "essay", "assignment", "invoice", "paper"):
            assert forbidden.lower() not in line_item_name.lower()

    @patch("payments_processor.providers.stripe._stripe")
    def test_refund_payment_satisfies_contract(self, mock_stripe_fn):
        stripe = MagicMock()
        stripe.checkout.Session.retrieve.return_value = MagicMock(payment_intent="pi_test")
        stripe.PaymentIntent.retrieve.return_value = self._mock_payment_intent()
        stripe.Refund.create.return_value = self._mock_refund()
        mock_stripe_fn.return_value = stripe

        result = self.provider.refund_payment(_refund_request(checkout_id="cs_test_abc"))
        _assert_refund_result_contract(result)

    @patch("payments_processor.providers.stripe._stripe")
    def test_verify_payment_satisfies_contract(self, mock_stripe_fn):
        stripe = MagicMock()
        session = self._mock_session()
        session.payment_status = "paid"
        session.amount_total = 5000
        session.currency = "usd"
        session.payment_intent = "pi_test"
        stripe.checkout.Session.retrieve.return_value = session
        mock_stripe_fn.return_value = stripe

        result = self.provider.verify_payment(_verification_request(checkout_id="cs_test_abc"))
        _assert_verification_result_contract(result)

    def test_webhook_parse_identifies_success_event(self):
        payload = {
            "id": "evt_success",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test",
                    "client_reference_id": "INFQ_abc123",
                    "payment_intent": "pi_test",
                    "amount_total": 5000,
                    "currency": "usd",
                    "metadata": {"merchant_reference": "INFQ_abc123"},
                }
            },
        }
        result = self.provider.parse_webhook(payload)
        assert result.status == "success"
        assert result.reference == "INFQ_abc123"

    def test_webhook_parse_identifies_failure_event(self):
        payload = {
            "id": "evt_fail",
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": "pi_fail",
                    "client_reference_id": "INFQ_abc456",
                    "amount": 5000,
                    "currency": "usd",
                    "metadata": {"merchant_reference": "INFQ_abc456"},
                }
            },
        }
        result = self.provider.parse_webhook(payload)
        assert result.status == "failed"
