from __future__ import annotations

from django.db.models import QuerySet

from billing.models.supporting_document import SupportingDocument


class SupportingDocumentSelector:
    """
    Provide read-side helpers and common queries for billing supporting
    documents.

    Supporting documents may be attached to invoices or payment
    requests. This selector keeps reusable read logic out of models and
    services.
    """

    @staticmethod
    def get_queryset_for_website(
        *,
        website,
    ) -> QuerySet[SupportingDocument]:
        """
        Return a tenant-scoped supporting document queryset.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[SupportingDocument]:
                Tenant-scoped supporting document queryset.
        """
        return SupportingDocument.objects.filter(website=website)

    @classmethod
    def get_queryset_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> QuerySet[SupportingDocument]:
        """
        Return supporting documents linked to an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose supporting documents should be returned.

        Returns:
            QuerySet[SupportingDocument]:
                Invoice-scoped supporting document queryset.
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
    ) -> QuerySet[SupportingDocument]:
        """
        Return supporting documents linked to a payment request.

        Args:
            website:
                Tenant website.
            payment_request:
                Payment request whose supporting documents should be
                returned.

        Returns:
            QuerySet[SupportingDocument]:
                Payment-request-scoped supporting document queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            payment_request=payment_request
        )

    @classmethod
    def get_latest_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> SupportingDocument | None:
        """
        Return the most recently created supporting document for an
        invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose latest supporting document should be
                returned.

        Returns:
            SupportingDocument | None:
                Latest supporting document if one exists, otherwise
                None.
        """
        return (
            cls.get_queryset_for_invoice(
                website=website,
                invoice=invoice,
            )
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def get_latest_for_payment_request(
        cls,
        *,
        website,
        payment_request,
    ) -> SupportingDocument | None:
        """
        Return the most recently created supporting document for a
        payment request.

        Args:
            website:
                Tenant website.
            payment_request:
                Payment request whose latest supporting document should
                be returned.

        Returns:
            SupportingDocument | None:
                Latest supporting document if one exists, otherwise
                None.
        """
        return (
            cls.get_queryset_for_payment_request(
                website=website,
                payment_request=payment_request,
            )
            .order_by("-created_at")
            .first()
        )