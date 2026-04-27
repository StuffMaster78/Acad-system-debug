from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from billing.constants import ReminderStatus
from billing.models.reminder import Reminder


class ReminderService:
    """
    Own reminder record write operations.

    This service records reminder attempts and outcomes. It does not
    decide reminder scheduling policy.
    """

    @staticmethod
    def _validate_target(
        *,
        invoice=None,
        payment_request=None,
    ) -> None:
        """
        Validate that a reminder has exactly one target.

        Args:
            invoice:
                Optional invoice target.
            payment_request:
                Optional payment request target.

        Raises:
            ValidationError:
                Raised when neither target is provided or both are
                provided at the same time.
        """
        has_invoice = invoice is not None
        has_payment_request = payment_request is not None

        if not has_invoice and not has_payment_request:
            raise ValidationError(
                "A reminder must target an invoice or payment request."
            )

        if has_invoice and has_payment_request:
            raise ValidationError(
                "A reminder cannot target both an invoice and a "
                "payment request."
            )

    @classmethod
    def create_reminder(
        cls,
        *,
        website,
        channel: str,
        event_key: str,
        invoice=None,
        payment_request=None,
        scheduled_for=None,
    ) -> Reminder:
        """
        Create a pending reminder record.

        Args:
            website:
                Tenant website that owns the reminder.
            channel:
                Delivery channel used for the reminder.
            event_key:
                Notification event key used for dispatch.
            invoice:
                Optional invoice target.
            payment_request:
                Optional payment request target.
            scheduled_for:
                Optional scheduled dispatch timestamp.

        Returns:
            Reminder:
                Newly created reminder record.

        Raises:
            ValidationError:
                Raised when the reminder target is invalid.
        """
        cls._validate_target(
            invoice=invoice,
            payment_request=payment_request,
        )

        return Reminder.objects.create(
            website=website,
            invoice=invoice,
            payment_request=payment_request,
            channel=channel,
            event_key=event_key,
            status=ReminderStatus.PENDING,
            scheduled_for=scheduled_for,
        )

    @classmethod
    @transaction.atomic
    def mark_sent(cls, *, reminder: Reminder) -> Reminder:
        """
        Mark a reminder as sent.

        Args:
            reminder:
                Reminder instance to update.

        Returns:
            Reminder:
                Updated reminder instance.
        """
        reminder.status = ReminderStatus.SENT
        reminder.sent_at = timezone.now()
        reminder.save(update_fields=["status", "sent_at", "updated_at"])
        return reminder

    @classmethod
    @transaction.atomic
    def mark_failed(
        cls,
        *,
        reminder: Reminder,
        error_message: str,
    ) -> Reminder:
        """
        Mark a reminder as failed.

        Args:
            reminder:
                Reminder instance to update.
            error_message:
                Failure detail to persist.

        Returns:
            Reminder:
                Updated reminder instance.
        """
        reminder.status = ReminderStatus.FAILED
        reminder.failed_at = timezone.now()
        reminder.error_message = error_message
        reminder.save(
            update_fields=[
                "status",
                "failed_at",
                "error_message",
                "updated_at",
            ]
        )
        return reminder
    

    @classmethod
    @transaction.atomic
    def mark_cancelled(cls, *, reminder: Reminder) -> Reminder:
        """
        Mark a reminder as cancelled.

        Args:
            reminder:
                Reminder instance to update.

        Returns:
            Reminder:
                Updated reminder instance.

        Raises:
            ValidationError:
                Raised when the reminder is already in a terminal state.
        """
        if reminder.status in {
            ReminderStatus.SENT,
            ReminderStatus.FAILED,
            ReminderStatus.CANCELLED,
        }:
            raise ValidationError(
                "Reminder is already in a terminal state."
            )

        reminder.status = ReminderStatus.CANCELLED
        reminder.save(update_fields=["status", "updated_at"])
        return reminder