"""
Tests for ProviderRequestAssembler.

These tests are the privacy guarantee for the provider boundary.
A failing assertion here means business data could reach an external provider.
"""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from django.test import override_settings

from payments_processor.providers.base import (
    ProviderMetadata,
    ProviderPaymentRequest,
    ProviderRefundRequest,
    ProviderVerificationRequest,
)
from payments_processor.providers.mapper import ProviderRequestAssembler


INFOQ_BASE = "https://pay.infoq.com"


def _make_intent(
    *,
    reference: str = "INFQ_abc123",
    amount: Decimal = Decimal("99.99"),
    currency: str = "USD",
    purpose: str = "order",
    email: str = "client@example.com",
    provider_intent_id: str = "cs_test_abc",
    provider_transaction_id: str = "pi_test_abc",
) -> MagicMock:
    intent = MagicMock()
    intent.reference = reference
    intent.amount = amount
    intent.currency = currency
    intent.purpose = purpose
    intent.client.email = email
    intent.provider_intent_id = provider_intent_id
    intent.provider_transaction_id = provider_transaction_id
    return intent


# ---------------------------------------------------------------------------
# to_payment_request — field mapping
# ---------------------------------------------------------------------------

class TestToPaymentRequest:

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_merchant_reference_equals_intent_reference(self):
        intent = _make_intent(reference="INFQ_xyz789")
        req = ProviderRequestAssembler.to_payment_request(intent)
        assert req.merchant_reference == "INFQ_xyz789"

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_amount_copied(self):
        intent = _make_intent(amount=Decimal("149.50"))
        req = ProviderRequestAssembler.to_payment_request(intent)
        assert req.amount == Decimal("149.50")

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_currency_copied(self):
        intent = _make_intent(currency="GBP")
        req = ProviderRequestAssembler.to_payment_request(intent)
        assert req.currency == "GBP"

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_customer_email_copied(self):
        intent = _make_intent(email="student@uni.edu")
        req = ProviderRequestAssembler.to_payment_request(intent)
        assert req.customer_email == "student@uni.edu"

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_result_is_provider_payment_request(self):
        req = ProviderRequestAssembler.to_payment_request(_make_intent())
        assert isinstance(req, ProviderPaymentRequest)


# ---------------------------------------------------------------------------
# to_payment_request — relay URLs
# ---------------------------------------------------------------------------

class TestRelayUrls:

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_success_url_uses_infoq_domain(self):
        req = ProviderRequestAssembler.to_payment_request(_make_intent())
        assert req.success_url.startswith(INFOQ_BASE)

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_cancel_url_uses_infoq_domain(self):
        req = ProviderRequestAssembler.to_payment_request(_make_intent())
        assert req.cancel_url.startswith(INFOQ_BASE)

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_success_url_contains_reference(self):
        intent = _make_intent(reference="INFQ_abc123")
        req = ProviderRequestAssembler.to_payment_request(intent)
        assert "INFQ_abc123" in req.success_url

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_cancel_url_contains_reference(self):
        intent = _make_intent(reference="INFQ_abc123")
        req = ProviderRequestAssembler.to_payment_request(intent)
        assert "INFQ_abc123" in req.cancel_url

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_no_merchant_domain_in_success_url(self):
        req = ProviderRequestAssembler.to_payment_request(_make_intent())
        for domain in ("gradecrest", "essaymaniacs", "nursemygrade", "rpm"):
            assert domain not in req.success_url

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_no_merchant_domain_in_cancel_url(self):
        req = ProviderRequestAssembler.to_payment_request(_make_intent())
        for domain in ("gradecrest", "essaymaniacs", "nursemygrade", "rpm"):
            assert domain not in req.cancel_url


# ---------------------------------------------------------------------------
# to_payment_request — product name catalog
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("purpose,expected_name", [
    ("order",                   "InfoQ Digital Service"),
    ("order_payment",           "InfoQ Digital Service"),
    ("special_order",           "InfoQ Professional Service"),
    ("special_order_payment",   "InfoQ Professional Service"),
    ("invoice",                 "InfoQ Professional Service"),
    ("billing_payment_request", "InfoQ Professional Service"),
    ("wallet_top_up",           "InfoQ Wallet Credit"),
    ("class_purchase",          "InfoQ Digital Service"),
    ("class_order_payment",     "InfoQ Digital Service"),
    ("bundle_purchase",         "InfoQ Digital Service"),
    ("tip",                     "InfoQ Digital Service"),
    ("extra_order_charge",      "InfoQ Digital Service"),
    ("manual_billing",          "InfoQ Professional Service"),
    ("unknown_future_purpose",  "InfoQ Digital Service"),
])
@override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
def test_product_name_by_purpose(purpose, expected_name):
    intent = _make_intent(purpose=purpose)
    req = ProviderRequestAssembler.to_payment_request(intent)
    assert req.product_name == expected_name


# ---------------------------------------------------------------------------
# to_payment_request — ProviderMetadata privacy boundary
# ---------------------------------------------------------------------------

class TestProviderMetadataPrivacy:

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_metadata_is_provider_metadata_instance(self):
        req = ProviderRequestAssembler.to_payment_request(_make_intent())
        assert isinstance(req.metadata, ProviderMetadata)

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_metadata_contains_merchant_reference(self):
        intent = _make_intent(reference="INFQ_abc123")
        req = ProviderRequestAssembler.to_payment_request(intent)
        assert req.metadata.merchant_reference == "INFQ_abc123"

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_metadata_contains_environment(self):
        req = ProviderRequestAssembler.to_payment_request(_make_intent())
        assert req.metadata.environment == "production"

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="staging")
    def test_metadata_environment_reflects_setting(self):
        req = ProviderRequestAssembler.to_payment_request(_make_intent())
        assert req.metadata.environment == "staging"

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_metadata_is_immutable(self):
        req = ProviderRequestAssembler.to_payment_request(_make_intent())
        with pytest.raises((AttributeError, TypeError)):
            req.metadata.merchant_reference = "tampered"  # type: ignore[misc]

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_to_dict_contains_only_approved_keys(self):
        req = ProviderRequestAssembler.to_payment_request(_make_intent())
        d = req.metadata.to_dict()
        assert set(d.keys()) == {"merchant_reference", "environment"}

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_service_family_never_in_metadata(self):
        intent = _make_intent()
        intent.service_family = "academic_writing"
        req = ProviderRequestAssembler.to_payment_request(intent)
        d = req.metadata.to_dict()
        assert "service_family" not in d
        assert "academic_writing" not in str(d)

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_service_code_never_in_metadata(self):
        intent = _make_intent()
        intent.service_code = "essay"
        req = ProviderRequestAssembler.to_payment_request(intent)
        d = req.metadata.to_dict()
        assert "service_code" not in d
        assert "essay" not in str(d)

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_invoice_title_never_in_metadata(self):
        intent = _make_intent()
        req = ProviderRequestAssembler.to_payment_request(intent)
        d = req.metadata.to_dict()
        assert "invoice_title" not in d

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_website_never_in_metadata(self):
        intent = _make_intent()
        req = ProviderRequestAssembler.to_payment_request(intent)
        d = req.metadata.to_dict()
        assert "website" not in d

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_order_id_never_in_metadata(self):
        intent = _make_intent()
        req = ProviderRequestAssembler.to_payment_request(intent)
        d = req.metadata.to_dict()
        assert "order_id" not in d

    @override_settings(INFOQ_PAYMENT_BASE_URL=INFOQ_BASE, ENVIRONMENT="production")
    def test_no_business_terms_in_product_name_for_order(self):
        intent = _make_intent(purpose="order")
        req = ProviderRequestAssembler.to_payment_request(intent)
        forbidden = {"essay", "assignment", "research", "paper", "nursing", "class"}
        assert not forbidden.intersection(req.product_name.lower().split())


# ---------------------------------------------------------------------------
# to_refund_request
# ---------------------------------------------------------------------------

class TestToRefundRequest:

    def test_uses_provider_intent_id_as_checkout_id(self):
        intent = _make_intent(provider_intent_id="cs_test_xyz")
        req = ProviderRequestAssembler.to_refund_request(intent, Decimal("50.00"))
        assert req.provider_checkout_id == "cs_test_xyz"

    def test_uses_provider_transaction_id_as_payment_id(self):
        intent = _make_intent(provider_transaction_id="pi_test_xyz")
        req = ProviderRequestAssembler.to_refund_request(intent, Decimal("50.00"))
        assert req.provider_payment_id == "pi_test_xyz"

    def test_amount_copied(self):
        intent = _make_intent()
        req = ProviderRequestAssembler.to_refund_request(intent, Decimal("75.00"))
        assert req.amount == Decimal("75.00")

    def test_currency_copied(self):
        intent = _make_intent(currency="EUR")
        req = ProviderRequestAssembler.to_refund_request(intent, Decimal("50.00"))
        assert req.currency == "EUR"

    def test_merchant_reference_copied(self):
        intent = _make_intent(reference="INFQ_ref001")
        req = ProviderRequestAssembler.to_refund_request(intent, Decimal("50.00"))
        assert req.merchant_reference == "INFQ_ref001"

    def test_result_is_provider_refund_request(self):
        req = ProviderRequestAssembler.to_refund_request(_make_intent(), Decimal("50.00"))
        assert isinstance(req, ProviderRefundRequest)

    def test_fails_fast_when_both_provider_ids_empty(self):
        intent = _make_intent(provider_intent_id="", provider_transaction_id="")
        with pytest.raises(ValueError, match="no provider reference"):
            ProviderRequestAssembler.to_refund_request(intent, Decimal("50.00"))

    def test_succeeds_with_only_checkout_id(self):
        intent = _make_intent(provider_intent_id="cs_test_only", provider_transaction_id="")
        req = ProviderRequestAssembler.to_refund_request(intent, Decimal("50.00"))
        assert req.provider_checkout_id == "cs_test_only"
        assert req.provider_payment_id == ""

    def test_succeeds_with_only_payment_id(self):
        intent = _make_intent(provider_intent_id="", provider_transaction_id="pi_test_only")
        req = ProviderRequestAssembler.to_refund_request(intent, Decimal("50.00"))
        assert req.provider_checkout_id == ""
        assert req.provider_payment_id == "pi_test_only"


# ---------------------------------------------------------------------------
# to_verification_request
# ---------------------------------------------------------------------------

class TestToVerificationRequest:

    def test_uses_provider_intent_id_as_checkout_id(self):
        intent = _make_intent(provider_intent_id="cs_test_verify")
        req = ProviderRequestAssembler.to_verification_request(intent)
        assert req.provider_checkout_id == "cs_test_verify"

    def test_uses_provider_transaction_id_as_payment_id(self):
        intent = _make_intent(provider_transaction_id="pi_test_verify")
        req = ProviderRequestAssembler.to_verification_request(intent)
        assert req.provider_payment_id == "pi_test_verify"

    def test_merchant_reference_copied(self):
        intent = _make_intent(reference="INFQ_verify001")
        req = ProviderRequestAssembler.to_verification_request(intent)
        assert req.merchant_reference == "INFQ_verify001"

    def test_result_is_provider_verification_request(self):
        req = ProviderRequestAssembler.to_verification_request(_make_intent())
        assert isinstance(req, ProviderVerificationRequest)

    def test_fails_fast_when_both_provider_ids_empty(self):
        intent = _make_intent(provider_intent_id="", provider_transaction_id="")
        with pytest.raises(ValueError, match="no provider reference"):
            ProviderRequestAssembler.to_verification_request(intent)
