from __future__ import annotations

from django.db.models import QuerySet
from django.utils import timezone

from billing.constants import PaymentRequestStatus
from billing.models import PaymentRequest


class PaymentRequestSelector:
    """
    Provide read-side helpers and common payment request queries.

    This selector centralizes reusable read logic and computed checks
    for payment requests.
    """

    ACTIVE_STATUSES = {
        PaymentRequestStatus.DRAFT,
        PaymentRequestStatus.ISSUED,
        PaymentRequestStatus.PARTIALLY_PAID,
    }

    TERMINAL_STATUSES = {
        PaymentRequestStatus.PAID,
        PaymentRequestStatus.CANCELLED,
        PaymentRequestStatus.EXPIRED,
    }

    @staticmethod
    def get_recipient_email(
        *,
        payment_request: PaymentRequest,
    ) -> str:
        """
        Resolve the best recipient email for a payment request.

        Args:
            payment_request:
                Payment request to inspect.

        Returns:
            str: Resolved recipient email or an empty string.
        """
        if payment_request.client and payment_request.client.email:
            return payment_request.client.email

        return payment_request.recipient_email or ""

    @staticmethod
    def get_recipient_name(
        *,
        payment_request: PaymentRequest,
    ) -> str:
        """
        Resolve the best display name for a payment request recipient.

        Args:
            payment_request:
                Payment request to inspect.

        Returns:
            str: Best available recipient display name.
        """
        if payment_request.client:
            full_name = payment_request.client.get_full_name()
            if full_name:
                return full_name

            username = getattr(payment_request.client, "username", "")
            if username:
                return username

        if payment_request.recipient_name:
            return payment_request.recipient_name

        email = PaymentRequestSelector.get_recipient_email(
            payment_request=payment_request
        )
        if email and "@" in email:
            return email.split("@")[0]

        return "Recipient"

    @staticmethod
    def is_overdue(
        *,
        payment_request: PaymentRequest,
    ) -> bool:
        """
        Determine whether a payment request is overdue.

        Args:
            payment_request:
                Payment request to inspect.

        Returns:
            bool: True when the request is overdue and still payable.
        """
        if payment_request.status in {
            PaymentRequestStatus.PAID,
            PaymentRequestStatus.CANCELLED,
            PaymentRequestStatus.EXPIRED,
        }:
            return False

        if payment_request.due_at is None:
            return False

        return timezone.now() > payment_request.due_at

    @staticmethod
    def get_queryset_for_website(
        *,
        website,
    ) -> QuerySet[PaymentRequest]:
        """
        Return a tenant-scoped payment request queryset.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[PaymentRequest]:
                Tenant-scoped queryset.
        """
        return PaymentRequest.objects.filter(website=website)

    @classmethod
    def get_active_queryset_for_website(
        cls,
        *,
        website,
    ) -> QuerySet[PaymentRequest]:
        """
        Return active (payable) payment requests for a tenant.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[PaymentRequest]:
                Active payment requests queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status__in=cls.ACTIVE_STATUSES
        )

    @classmethod
    def get_overdue_queryset_for_website(
        cls,
        *,
        website,
    ) -> QuerySet[PaymentRequest]:
        """
        Return overdue payment requests for a tenant.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[PaymentRequest]:
                Overdue payment request queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status__in=cls.ACTIVE_STATUSES,
            due_at__isnull=False,
            due_at__lt=timezone.now(),
        )
    



    @staticmethod
    def is_token_valid(*, payment_request: PaymentRequest) -> bool:
        """
        Determine whether the payment request token is valid.

        Args:
            payment_request:
                Payment request to inspect.

        Returns:
            bool:
                True when a token exists and is not expired.
        """
        if not payment_request.payment_token:
            return False

        if payment_request.token_expires_at is None:
            return False

        return timezone.now() < payment_request.token_expires_at
    

    @classmethod
    def get_queryset_for_client(
        cls,
        *,
        website,
        client,
    ) -> QuerySet[PaymentRequest]:
        """
        Return payment requests for a specific client within a tenant.

        Args:
            website:
                Tenant website.
            client:
                Client whose payment requests should be returned.

        Returns:
            QuerySet[PaymentRequest]:
                Client-scoped payment request queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            client=client
        )