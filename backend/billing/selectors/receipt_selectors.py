from __future__ import annotations

from django.db.models import QuerySet

from billing.constants import ReceiptStatus
from billing.models.receipt import Receipt


class ReceiptSelector:
    """
    Provide read-side helpers and common receipt queries.

    This selector centralizes reusable read logic for tenant-scoped
    receipt access across billing, support, and client views.
    """

    @staticmethod
    def get_queryset_for_website(
        *,
        website,
    ) -> QuerySet[Receipt]:
        """
        Return a tenant-scoped receipt queryset.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[Receipt]:
                Tenant-scoped receipt queryset.
        """
        return Receipt.objects.filter(website=website)

    @classmethod
    def get_queryset_for_client(
        cls,
        *,
        website,
        client,
    ) -> QuerySet[Receipt]:
        """
        Return receipts for a specific client within a tenant.

        Args:
            website:
                Tenant website.
            client:
                Client whose receipts should be returned.

        Returns:
            QuerySet[Receipt]:
                Client-scoped receipt queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            client=client
        )

    @classmethod
    def get_queryset_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> QuerySet[Receipt]:
        """
        Return receipts linked to an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose receipts should be returned.

        Returns:
            QuerySet[Receipt]:
                Invoice-scoped receipt queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            invoice=invoice
        )

    @classmethod
    def get_queryset_for_payment_request(
        cls,
        *,
        website,
        payment_request,
    ) -> QuerySet[Receipt]:
        """
        Return receipts linked to a billing payment request.

        Args:
            website:
                Tenant website.
            payment_request:
                Payment request whose receipts should be returned.

        Returns:
            QuerySet[Receipt]:
                Payment-request-scoped receipt queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            payment_request=payment_request
        )

    @classmethod
    def get_issued_queryset_for_website(
        cls,
        *,
        website,
    ) -> QuerySet[Receipt]:
        """
        Return issued receipts for a tenant.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[Receipt]:
                Issued receipt queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status=ReceiptStatus.ISSUED
        )

    @classmethod
    def get_voided_queryset_for_website(
        cls,
        *,
        website,
    ) -> QuerySet[Receipt]:
        """
        Return voided receipts for a tenant.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[Receipt]:
                Voided receipt queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status=ReceiptStatus.VOIDED
        )

    @classmethod
    def get_queryset_for_payment_intent_reference(
        cls,
        *,
        website,
        payment_intent_reference: str,
    ) -> QuerySet[Receipt]:
        """
        Return receipts linked to a payment intent reference.

        Args:
            website:
                Tenant website.
            payment_intent_reference:
                Payment intent reference to match.

        Returns:
            QuerySet[Receipt]:
                Payment-intent-scoped receipt queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            payment_intent_reference=payment_intent_reference
        )

    @classmethod
    def get_queryset_for_external_reference(
        cls,
        *,
        website,
        external_reference: str,
    ) -> QuerySet[Receipt]:
        """
        Return receipts linked to an external provider reference.

        Args:
            website:
                Tenant website.
            external_reference:
                External payment reference to match.

        Returns:
            QuerySet[Receipt]:
                External-reference-scoped receipt queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            external_reference=external_reference
        )

    @classmethod
    def get_latest_for_client(
        cls,
        *,
        website,
        client,
    ) -> Receipt | None:
        """
        Return the most recent receipt for a client within a tenant.

        Args:
            website:
                Tenant website.
            client:
                Client whose latest receipt should be returned.

        Returns:
            Receipt | None:
                Most recent client receipt if one exists, otherwise None.
        """
        return (
            cls.get_queryset_for_client(
                website=website,
                client=client,
            )
            .order_by("-issued_at", "-created_at")
            .first()
        )

    @classmethod
    def get_latest_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> Receipt | None:
        """
        Return the most recent receipt for an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose latest receipt should be returned.

        Returns:
            Receipt | None:
                Most recent invoice receipt if one exists, otherwise
                None.
        """
        return (
            cls.get_queryset_for_invoice(
                website=website,
                invoice=invoice,
            )
            .order_by("-issued_at", "-created_at")
            .first()
        )

    @classmethod
    def get_latest_for_payment_request(
        cls,
        *,
        website,
        payment_request,
    ) -> Receipt | None:
        """
        Return the most recent receipt for a payment request.

        Args:
            website:
                Tenant website.
            payment_request:
                Payment request whose latest receipt should be returned.

        Returns:
            Receipt | None:
                Most recent payment request receipt if one exists,
                otherwise None.
        """
        return (
            cls.get_queryset_for_payment_request(
                website=website,
                payment_request=payment_request,
            )
            .order_by("-issued_at", "-created_at")
            .first()
        )

    @staticmethod
    def is_issued(
        *,
        receipt: Receipt,
    ) -> bool:
        """
        Determine whether a receipt is issued.

        Args:
            receipt:
                Receipt to inspect.

        Returns:
            bool:
                True when the receipt is currently issued.
        """
        return receipt.status == ReceiptStatus.ISSUED

    @staticmethod
    def is_voided(
        *,
        receipt: Receipt,
    ) -> bool:
        """
        Determine whether a receipt is voided.

        Args:
            receipt:
                Receipt to inspect.

        Returns:
            bool:
                True when the receipt is currently voided.
        """
        return receipt.status == ReceiptStatus.VOIDED