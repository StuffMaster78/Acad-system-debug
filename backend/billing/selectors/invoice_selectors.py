from __future__ import annotations

from django.db.models import QuerySet
from django.utils import timezone

from billing.models.invoice import Invoice, InvoiceStatus


class InvoiceSelector:
    """
    Read side helper for invoice queries and computed invoice information.

    This selector layer keeps non mutating logic out of the model and service.
    It is responsible for:
        1. Common query patterns
        2. Derived invoice read state
        3. Recipient resolution helpers
        4. Safe filtering for dashboards and workflows
    """

    @staticmethod
    def get_recipient_email(*, invoice: Invoice) -> str:
        """
        Provide read-side helpers and common invoice queries.

        This selector keeps computed reads and recurring query patterns
        out of the model and service layer.
        Resolve the best recipient email for an invoice.

        Resolution order:
            1. Linked client email
            2. Stored recipient_email

        Args:
            invoice: Invoice instance to inspect.

        Returns:
            str: Resolved recipient email, or an empty string if unavailable.
        """
        if invoice.client and invoice.client.email:
            return invoice.client.email
        return invoice.recipient_email or ""

    @staticmethod
    def get_recipient_name(*, invoice: Invoice) -> str:
        """
        Resolve the best display name for an invoice recipient.

        Resolution order:
            1. Client full name
            2. Client username
            3. Stored recipient_name
            4. Local part of recipient email
            5. Generic fallback

        Args:
            invoice: Invoice instance to inspect.

        Returns:
            str: Resolved display name.
        """
        if invoice.client:
            full_name = invoice.client.get_full_name()
            if full_name:
                return full_name

            username = getattr(invoice.client, "username", "")
            if username:
                return username

        if invoice.recipient_name:
            return invoice.recipient_name

        email = InvoiceSelector.get_recipient_email(invoice=invoice)
        if email and "@" in email:
            return email.split("@")[0]

        return "Customer"

    @staticmethod
    def is_paid(*, invoice: Invoice) -> bool:
        """
        Determine whether the invoice is fully paid.

        Args:
            invoice: Invoice instance to inspect.

        Returns:
            bool: True when the invoice status is paid, else False.
        """
        return invoice.status == InvoiceStatus.PAID

    @staticmethod
    def is_overdue(*, invoice: Invoice) -> bool:
        """
        Determine whether the invoice is overdue.

        An invoice is considered overdue when the current time is later
        than due_at and the invoice is still payable.

        Args:
            invoice: Invoice instance to inspect.

        Returns:
            bool: True if the invoice is overdue, else False.
        """
        if invoice.status in {
            InvoiceStatus.PAID,
            InvoiceStatus.CANCELLED,
            InvoiceStatus.EXPIRED,
        }:
            return False

        return timezone.now() > invoice.due_at

    @staticmethod
    def is_token_valid(*, invoice: Invoice) -> bool:
        """
        Determine whether the invoice payment token is currently valid.

        Args:
            invoice: Invoice instance to inspect.

        Returns:
            bool: True if the token exists and is not expired.
        """
        if not invoice.payment_token or not invoice.token_expires_at:
            return False
        return timezone.now() < invoice.token_expires_at

    @staticmethod
    def get_queryset_for_website(*, website) -> QuerySet[Invoice]:
        """
        Get the base invoice queryset scoped to a single tenant.

        Args:
            website: Tenant website.

        Returns:
            QuerySet[Invoice]: Website scoped invoice queryset.
        """
        return Invoice.objects.filter(website=website)

    @classmethod
    def get_unpaid_queryset_for_website(cls, *, website) -> QuerySet[Invoice]:
        """
        Get unpaid and still actionable invoices for a website.

        Args:
            website: Tenant website.

        Returns:
            QuerySet[Invoice]: Queryset of draft, issued, and partially paid invoices.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status__in=[
                InvoiceStatus.DRAFT,
                InvoiceStatus.ISSUED,
                InvoiceStatus.PARTIALLY_PAID,
            ]
        )

    @classmethod
    def get_overdue_queryset_for_website(cls, *, website) -> QuerySet[Invoice]:
        """
        Get overdue invoices for a tenant website.

        Args:
            website: Tenant website.

        Returns:
            QuerySet[Invoice]: Queryset of overdue invoices.
        """
        return cls.get_unpaid_queryset_for_website(
            website=website
        ).filter(due_at__lt=timezone.now())

    @classmethod
    def get_client_invoices(
        cls,
        *,
        website,
        client,
    ) -> QuerySet[Invoice]:
        """
        Get invoices for a client within a tenant.

        Args:
            website: Tenant website.
            client: Recipient user.

        Returns:
            QuerySet[Invoice]: Queryset of invoices belonging to the client.
        """
        return cls.get_queryset_for_website(website=website).filter(
            client=client
        )

    @classmethod
    def get_by_reference(
        cls,
        *,
        website,
        reference: str,
    ) -> Invoice:
        """
        Retrieve a single invoice by tenant and human readable reference.

        Args:
            website: Tenant website.
            reference: Invoice reference string.

        Returns:
            Invoice: Matching invoice instance.
        """
        return cls.get_queryset_for_website(website=website).get(
            reference=reference
        )

    @classmethod
    def get_by_payment_token(
        cls,
        *,
        payment_token: str,
    ) -> Invoice:
        """
        Retrieve a single invoice by payment token.

        Args:
            payment_token: Invoice payment token.

        Returns:
            Invoice: Matching invoice instance.
        """
        return Invoice.objects.get(payment_token=payment_token)
    

    @classmethod
    def get_queryset_for_client(
        cls,
        *,
        website,
        client,
    ) -> QuerySet[Invoice]:
        """
        Return invoices for a specific client within a tenant.

        Args:
            website:
                Tenant website.
            client:
                Client whose invoices should be returned.

        Returns:
            QuerySet[Invoice]:
                Client-scoped invoice queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            client=client
        )