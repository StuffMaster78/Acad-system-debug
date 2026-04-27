from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from billing.constants import ReceiptStatus
from billing.models.receipt import Receipt


class ReceiptService:
    """
    Own receipt write operations and lifecycle transitions.

    This service manages local receipt creation and lifecycle changes.
    It does not verify payments, coordinate settlement, or send emails.
    """

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        """
        Validate that a receipt amount is greater than zero.

        Args:
            amount:
                Amount to validate.

        Raises:
            ValidationError:
                Raised when amount is zero or negative.
        """
        if amount <= Decimal("0"):
            raise ValidationError(
                "Receipt amount must be greater than zero."
            )

    @staticmethod
    def _validate_target(
        *,
        invoice=None,
        payment_request=None,
    ) -> None:
        """
        Validate receipt target selection.

        Args:
            invoice:
                Optional invoice target.
            payment_request:
                Optional payment request target.

        Raises:
            ValidationError:
                Raised when neither target is supplied or both are
                supplied.
        """
        has_invoice = invoice is not None
        has_payment_request = payment_request is not None

        if not has_invoice and not has_payment_request:
            raise ValidationError(
                "A receipt must target an invoice or payment request."
            )

        if has_invoice and has_payment_request:
            raise ValidationError(
                "A receipt cannot target both an invoice and a payment "
                "request."
            )

    @staticmethod
    def _build_title_snapshot(
        *,
        invoice=None,
        payment_request=None,
    ) -> str:
        """
        Build a human-readable title snapshot for the receipt.

        Args:
            invoice:
                Optional invoice target.
            payment_request:
                Optional payment request target.

        Returns:
            str:
                Short description of what the payment covered.
        """
        if invoice is not None:
            return invoice.title

        if payment_request is not None:
            return payment_request.title

        return "Payment Receipt"

    @staticmethod
    def _build_description_snapshot(
        *,
        invoice=None,
        payment_request=None,
    ) -> str:
        """
        Build a detailed description snapshot for the receipt.

        Args:
            invoice:
                Optional invoice target.
            payment_request:
                Optional payment request target.

        Returns:
            str:
                Human-readable description of what the payment covered.
        """
        if invoice is not None:
            if invoice.description:
                return invoice.description
            return f"Payment received for invoice {invoice.reference}."

        if payment_request is not None:
            if payment_request.description:
                return payment_request.description
            return (
                "Payment received for billing payment request "
                f"{payment_request.reference}."
            )

        return ""

    @staticmethod
    def _build_company_name_snapshot(*, website) -> str:
        """
        Resolve tenant company or brand name for receipt snapshot.

        Args:
            website:
                Tenant website instance.

        Returns:
            str:
                Best available tenant company or brand name.
        """
        for attr_name in (
            "company_name",
            "brand_name",
            "name",
            "title",
        ):
            value = getattr(website, attr_name, "")
            if value:
                return str(value)

        return ""

    @staticmethod
    def _build_website_name_snapshot(*, website) -> str:
        """
        Resolve website display name for receipt snapshot.

        Args:
            website:
                Tenant website instance.

        Returns:
            str:
                Best available website display name.
        """
        for attr_name in ("name", "title", "brand_name"):
            value = getattr(website, attr_name, "")
            if value:
                return str(value)

        return ""

    @staticmethod
    def _build_website_domain_snapshot(*, website) -> str:
        """
        Resolve website domain for receipt snapshot.

        Args:
            website:
                Tenant website instance.

        Returns:
            str:
                Best available website domain or hostname.
        """
        for attr_name in ("domain", "host", "hostname", "url"):
            value = getattr(website, attr_name, "")
            if value:
                return str(value)

        return ""

    @staticmethod
    def _build_support_email_snapshot(*, website) -> str:
        """
        Resolve tenant support email for receipt snapshot.

        Args:
            website:
                Tenant website instance.

        Returns:
            str:
                Best available tenant support email.
        """
        for attr_name in (
            "support_email",
            "contact_email",
            "email",
        ):
            value = getattr(website, attr_name, "")
            if value:
                return str(value)

        return ""

    @classmethod
    @transaction.atomic
    def issue_receipt(
        cls,
        *,
        website,
        amount: Decimal,
        currency: str = "",
        client=None,
        recipient_email: str = "",
        recipient_name: str = "",
        invoice=None,
        payment_request=None,
        payment_intent_reference: str = "",
        external_reference: str = "",
        payment_provider: str = "",
    ) -> Receipt:
        """
        Create and issue a tenant-aware receipt.

        Args:
            website:
                Tenant website that owns the receipt.
            amount:
                Settled amount acknowledged by the receipt.
            currency:
                Currency code for the settled amount.
            client:
                Optional linked user recipient.
            recipient_email:
                Fallback recipient email.
            recipient_name:
                Display name for the recipient.
            invoice:
                Optional invoice target.
            payment_request:
                Optional payment request target.
            payment_intent_reference:
                Payment intent reference tied to the receipt.
            external_reference:
                External provider reference tied to settlement.
            payment_provider:
                Payment provider used for the settlement.

        Returns:
            Receipt:
                Newly issued receipt.

        Raises:
            ValidationError:
                Raised when target or amount validation fails.
        """
        cls._validate_amount(amount=amount)
        cls._validate_target(
            invoice=invoice,
            payment_request=payment_request,
        )

        return Receipt.objects.create(
            website=website,
            amount=amount,
            currency=currency,
            client=client,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            invoice=invoice,
            payment_request=payment_request,
            title_snapshot=cls._build_title_snapshot(
                invoice=invoice,
                payment_request=payment_request,
            ),
            description_snapshot=cls._build_description_snapshot(
                invoice=invoice,
                payment_request=payment_request,
            ),
            company_name_snapshot=cls._build_company_name_snapshot(
                website=website
            ),
            website_name_snapshot=cls._build_website_name_snapshot(
                website=website
            ),
            website_domain_snapshot=cls._build_website_domain_snapshot(
                website=website
            ),
            support_email_snapshot=cls._build_support_email_snapshot(
                website=website
            ),
            payment_intent_reference=payment_intent_reference,
            external_reference=external_reference,
            payment_provider=payment_provider,
            status=ReceiptStatus.ISSUED,
            issued_at=timezone.now(),
        )

    @classmethod
    @transaction.atomic
    def void_receipt(
        cls,
        *,
        receipt: Receipt,
        voided_at=None,
    ) -> Receipt:
        """
        Void an issued receipt.

        Args:
            receipt:
                Receipt instance to update.
            voided_at:
                Optional explicit void timestamp.

        Returns:
            Receipt:
                Updated voided receipt.

        Raises:
            ValidationError:
                Raised when the receipt is already voided.
        """
        if receipt.status == ReceiptStatus.VOIDED:
            raise ValidationError("Receipt is already voided.")

        receipt.status = ReceiptStatus.VOIDED
        receipt.voided_at = voided_at or timezone.now()
        receipt.save(update_fields=["status", "voided_at", "updated_at"])
        return receipt