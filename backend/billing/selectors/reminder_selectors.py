from __future__ import annotations

from django.db.models import QuerySet
from django.utils import timezone

from billing.constants import ReminderStatus
from billing.models.reminder import Reminder


class ReminderSelector:
    """
    Provide read side helpers and common reminder queries.
    """

    @staticmethod
    def get_queryset_for_website(*, website) -> QuerySet[Reminder]:
        """
        Return a tenant scoped reminder queryset.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[Reminder]:
                Tenant scoped reminder queryset.
        """
        return Reminder.objects.filter(website=website)

    @classmethod
    def get_pending_queryset_for_website(
        cls,
        *,
        website,
    ) -> QuerySet[Reminder]:
        """
        Return pending reminders for a tenant.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[Reminder]:
                Pending reminder queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status=ReminderStatus.PENDING
        )

    @classmethod
    def get_due_queryset_for_website(
        cls,
        *,
        website,
    ) -> QuerySet[Reminder]:
        """
        Return reminders whose scheduled time is due.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[Reminder]:
                Due reminder queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status=ReminderStatus.PENDING,
            scheduled_for__isnull=False,
            scheduled_for__lte=timezone.now(),
        )

    @classmethod
    def get_queryset_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> QuerySet[Reminder]:
        """
        Return reminders linked to an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice target.

        Returns:
            QuerySet[Reminder]:
                Invoice scoped reminder queryset.
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
    ) -> QuerySet[Reminder]:
        """
        Return reminders linked to a payment request.

        Args:
            website:
                Tenant website.
            payment_request:
                Payment request target.

        Returns:
            QuerySet[Reminder]:
                Payment request scoped reminder queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            payment_request=payment_request
        )