from __future__ import annotations

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from billing.constants import (
    ReminderStatus,
    PaymentRequestStatus,
    InvoiceStatus,
)
from billing.models.invoice import Invoice
from billing.models.payment_request import PaymentRequest
from billing.models.reminder import Reminder
from billing.services.reminder_service import ReminderService
from notifications_system.services.notification_service import (
    NotificationService,
)
from billing.selectors.payment_installment_selectors import (
    PaymentInstallmentSelector,
)
from audit_logging.services.audit_log_service import AuditLogService

class ReminderOrchestrationService:
    """
    Coordinate reminder creation, dispatch, and cancellation for
    unpaid billing artifacts.

    Reminders are sent before expiry or cancellation workflows.
    """

    @staticmethod
    def _validate_receivable_target(
        *,
        invoice: Invoice | None = None,
        payment_request: PaymentRequest | None = None,
    ) -> None:
        """
        Validate reminder target selection.

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
                "Reminder target requires an invoice or payment request."
            )

        if has_invoice and has_payment_request:
            raise ValidationError(
                "Reminder target cannot be both invoice and payment "
                "request."
            )

    @staticmethod
    def _is_invoice_remindable(*, invoice: Invoice) -> bool:
        """
        Determine whether an invoice is still remindable.

        Args:
            invoice:
                Invoice to inspect.

        Returns:
            bool:
                True when invoice is not terminal.
        """
        return invoice.status in {
            InvoiceStatus.DRAFT,
            InvoiceStatus.ISSUED,
            InvoiceStatus.PARTIALLY_PAID,
        }

    @staticmethod
    def _is_payment_request_remindable(
        *,
        payment_request: PaymentRequest,
    ) -> bool:
        """
        Determine whether a payment request is still remindable.

        Args:
            payment_request:
                Payment request to inspect.

        Returns:
            bool:
                True when payment request is not terminal.
        """
        return payment_request.status in {
            "draft",
            "issued",
            "partially_paid",
        }

    @staticmethod
    def _build_context(
        *,
        invoice: Invoice | None = None,
        payment_request: PaymentRequest | None = None,
    ) -> dict:
        """
        Build notification context for reminder dispatch.

        Args:
            invoice:
                Optional invoice target.
            payment_request:
                Optional payment request target.

        Returns:
            dict:
                Reminder notification context.
        """
        if invoice is not None:
            return {
                "invoice_id": invoice.pk,
                "invoice_reference": invoice.reference,
                "invoice_title": invoice.title,
                "amount": str(invoice.amount),
                "currency": invoice.currency,
                "due_at": (
                    invoice.due_at.isoformat()
                    if invoice.due_at is not None
                    else ""
                ),
            }

        assert payment_request is not None

        return {
            "payment_request_id": payment_request.pk,
            "payment_request_reference": payment_request.reference,
            "payment_request_title": payment_request.title,
            "amount": str(payment_request.amount),
            "currency": payment_request.currency,
            "due_at": (
                payment_request.due_at.isoformat()
                if payment_request.due_at is not None
                else ""
            ),
        }

    @classmethod
    def schedule_invoice_reminder(
        cls,
        *,
        invoice: Invoice,
        event_key: str = "billing.invoice.reminder",
        channel: str = "email",
        scheduled_for=None,
    ) -> Reminder:
        """
        Create a reminder record for an invoice.

        Args:
            invoice:
                Invoice to remind.
            event_key:
                Notification event key.
            channel:
                Delivery channel.
            scheduled_for:
                Optional dispatch timestamp.

        Returns:
            Reminder:
                Newly created reminder record.
        """
        cls._validate_receivable_target(invoice=invoice)

        if not cls._is_invoice_remindable(invoice=invoice):
            raise ValidationError(
                "Terminal invoices cannot receive reminders."
            )

        return ReminderService.create_reminder(
            website=invoice.website,
            invoice=invoice,
            channel=channel,
            event_key=event_key,
            scheduled_for=scheduled_for,
        )

    @classmethod
    def schedule_payment_request_reminder(
        cls,
        *,
        payment_request: PaymentRequest,
        event_key: str = "billing.payment_request.reminder",
        channel: str = "email",
        scheduled_for=None,
    ) -> Reminder:
        """
        Create a reminder record for a payment request.

        Args:
            payment_request:
                Payment request to remind.
            event_key:
                Notification event key.
            channel:
                Delivery channel.
            scheduled_for:
                Optional dispatch timestamp.

        Returns:
            Reminder:
                Newly created reminder record.
        """
        cls._validate_receivable_target(payment_request=payment_request)

        if not cls._is_payment_request_remindable(
            payment_request=payment_request
        ):
            raise ValidationError(
                "Terminal payment requests cannot receive reminders."
            )

        return ReminderService.create_reminder(
            website=payment_request.website,
            payment_request=payment_request,
            channel=channel,
            event_key=event_key,
            scheduled_for=scheduled_for,
        )

    @classmethod
    @transaction.atomic
    def dispatch_reminder(
        cls,
        *,
        reminder: Reminder,
        triggered_by=None,
    ) -> Reminder:
        """
        Dispatch a reminder through the notification system.

        Args:
            reminder:
                Reminder record to dispatch.
            triggered_by:
                Optional actor associated with dispatch.

        Returns:
            Reminder:
                Updated reminder record.

        Raises:
            ValidationError:
                Raised when the target is missing.
        """
        invoice = reminder.invoice
        payment_request = reminder.payment_request

        cls._validate_receivable_target(
            invoice=invoice,
            payment_request=payment_request,
        )

        website = reminder.website
        recipient = None

        if invoice is not None:
            if not cls._is_invoice_remindable(invoice=invoice):
                cancelled = ReminderService.mark_cancelled(
                    reminder=reminder
                )
                AuditLogService.log(
                    action="billing.reminder.cancelled",
                    actor=triggered_by,
                    target=cancelled,
                    website=website,
                    metadata={
                        "reason": "invoice_not_remindable",
                        "invoice_id": invoice.pk,
                        "invoice_reference": invoice.reference,
                    },
                )
                return cancelled

            recipient = invoice.client
            installment = PaymentInstallmentSelector.get_next_due_for_invoice(
                website=invoice.website,
                invoice=invoice,
            )

            if (
                reminder.event_key in {
                    "billing.installment.upcoming",
                    "billing.installment.due",
                    "billing.installment.overdue",
                }
                and installment is not None
            ):
                context = cls._build_installment_context(
                    installment=installment,
                    invoice=invoice,
                )
            else:
                context = cls._build_context(invoice=invoice)

        else:
            assert payment_request is not None

            if not cls._is_payment_request_remindable(
                payment_request=payment_request
            ):
                cancelled = ReminderService.mark_cancelled(
                    reminder=reminder
                )
                AuditLogService.log(
                    action="billing.reminder.cancelled",
                    actor=triggered_by,
                    target=cancelled,
                    website=website,
                    metadata={
                        "reason": "payment_request_not_remindable",
                        "payment_request_id": payment_request.pk,
                        "payment_request_reference": (
                            payment_request.reference
                        ),
                    },
                )
                return cancelled

            recipient = payment_request.client
            context = cls._build_context(
                payment_request=payment_request
            )

        if recipient is None:
            updated = ReminderService.mark_failed(
                reminder=reminder,
                error_message="Reminder recipient could not be resolved.",
            )
            AuditLogService.log(
                action="billing.reminder.failed",
                actor=triggered_by,
                target=updated,
                website=website,
                metadata={
                    "event_key": reminder.event_key,
                    "channel": reminder.channel,
                    "error": "Reminder recipient could not be resolved.",
                },
            )
            return updated

        try:
            NotificationService.notify(
                event_key=reminder.event_key,
                recipient=recipient,
                website=website,
                triggered_by=triggered_by,
                context=context,
            )

            updated = ReminderService.mark_sent(reminder=reminder)

            AuditLogService.log(
                action="billing.reminder.sent",
                actor=triggered_by,
                target=updated,
                website=website,
                metadata={
                    "event_key": reminder.event_key,
                    "channel": reminder.channel,
                    "context": context,
                },
            )

            return updated

        except Exception as exc:
            updated = ReminderService.mark_failed(
                reminder=reminder,
                error_message=str(exc),
            )
            AuditLogService.log(
                action="billing.reminder.failed",
                actor=triggered_by,
                target=updated,
                website=website,
                metadata={
                    "event_key": reminder.event_key,
                    "channel": reminder.channel,
                    "error": str(exc),
                },
            )
            return updated                  

    @classmethod
    @transaction.atomic
    def cancel_pending_reminders_for_invoice(
        cls,
        *,
        invoice: Invoice,
    ) -> int:
        """
        Cancel pending reminders for an invoice.

        Args:
            invoice:
                Invoice whose pending reminders should be cancelled.

        Returns:
            int:
                Number of reminders cancelled.
        """
        reminders = Reminder.objects.filter(
            website=invoice.website,
            invoice=invoice,
            status=ReminderStatus.PENDING,
        )

        count = 0
        for reminder in reminders:
            ReminderService.mark_cancelled(reminder=reminder)
            count += 1

        return count

    @classmethod
    @transaction.atomic
    def cancel_pending_reminders_for_payment_request(
        cls,
        *,
        payment_request: PaymentRequest,
    ) -> int:
        """
        Cancel pending reminders for a payment request.

        Args:
            payment_request:
                Payment request whose pending reminders should be
                cancelled.

        Returns:
            int:
                Number of reminders cancelled.
        """
        reminders = Reminder.objects.filter(
            website=payment_request.website,
            payment_request=payment_request,
            status=ReminderStatus.PENDING,
        )

        count = 0
        for reminder in reminders:
            ReminderService.mark_cancelled(reminder=reminder)
            count += 1

        return count

    @staticmethod
    def suggest_default_schedule(
        *,
        due_at,
        days_before_due: int = 2,
    ):
        """
        Suggest a reminder dispatch timestamp before due date.

        Args:
            due_at:
                Due timestamp for the receivable.
            days_before_due:
                Number of days before due date to remind.

        Returns:
            datetime | None:
                Suggested reminder timestamp, or None when no due date
                exists.
        """
        if due_at is None:
            return None

        return due_at - timedelta(days=days_before_due)

    @staticmethod
    def is_due_now(*, reminder: Reminder) -> bool:
        """
        Determine whether a reminder is due for dispatch now.

        Args:
            reminder:
                Reminder instance to inspect.

        Returns:
            bool:
                True when reminder is pending and due now.
        """
        if reminder.status != ReminderStatus.PENDING:
            return False

        if reminder.scheduled_for is None:
            return True

        return reminder.scheduled_for <= timezone.now()
    


    @staticmethod
    def _build_installment_context(
        *,
        installment,
        invoice,
    ) -> dict:
        """
        Build installment-aware reminder context.

        Args:
            installment:
                Installment tied to the reminder context.
            invoice:
                Parent invoice for the installment.

        Returns:
            dict:
                Notification context for installment reminders.
        """
        remaining_amount = installment.amount - installment.amount_paid
        if remaining_amount < 0:
            remaining_amount = 0

        return {
            "invoice_id": invoice.pk,
            "invoice_reference": invoice.reference,
            "invoice_title": invoice.title,
            "invoice_amount": str(invoice.amount),
            "invoice_currency": invoice.currency,
            "invoice_due_at": (
                invoice.due_at.isoformat()
                if invoice.due_at is not None
                else ""
            ),
            "installment_id": installment.pk,
            "installment_sequence_number": installment.sequence_number,
            "installment_amount": str(installment.amount),
            "installment_amount_paid": str(installment.amount_paid),
            "installment_remaining_amount": str(remaining_amount),
            "installment_due_at": installment.due_at.isoformat(),
        }

    @classmethod
    def schedule_upcoming_installment_reminder(
        cls,
        *,
        invoice: Invoice,
        installment,
        channel: str = "email",
        event_key: str = "billing.installment.upcoming",
        scheduled_for=None,
    ) -> Reminder:
        """
        Create an installment-aware upcoming reminder linked to an
        invoice.

        Args:
            invoice:
                Invoice owning the installment.
            installment:
                Installment being reminded.
            channel:
                Delivery channel.
            event_key:
                Notification event key.
            scheduled_for:
                Optional dispatch timestamp.

        Returns:
            Reminder:
                Newly created reminder record.
        """
        cls._validate_receivable_target(invoice=invoice)

        if not cls._is_invoice_remindable(invoice=invoice):
            raise ValidationError(
                "Terminal invoices cannot receive reminders."
            )

        if installment.cancelled_at is not None or installment.paid_at is not None:
            raise ValidationError(
                "Only active unpaid installments can receive reminders."
            )
        
        existing_reminder = cls._find_existing_pending_reminder(
            website=invoice.website,
            invoice=invoice,
            event_key=event_key,
            scheduled_for=scheduled_for,
        )
        if existing_reminder is not None:
            return existing_reminder
        
        return ReminderService.create_reminder(
            website=invoice.website,
            invoice=invoice,
            channel=channel,
            event_key=event_key,
            scheduled_for=scheduled_for,
        )

    @classmethod
    def schedule_due_installment_reminder(
        cls,
        *,
        invoice: Invoice,
        installment,
        channel: str = "email",
        event_key: str = "billing.installment.due",
        scheduled_for=None,
    ) -> Reminder:
        """
        Create an installment-aware due reminder linked to an invoice.

        Args:
            invoice:
                Invoice owning the installment.
            installment:
                Installment being reminded.
            channel:
                Delivery channel.
            event_key:
                Notification event key.
            scheduled_for:
                Optional dispatch timestamp.

        Returns:
            Reminder:
                Newly created reminder record.
        """
        return cls.schedule_upcoming_installment_reminder(
            invoice=invoice,
            installment=installment,
            channel=channel,
            event_key=event_key,
            scheduled_for=scheduled_for,
        )
    
    @classmethod
    def ensure_next_installment_upcoming_reminder(
        cls,
        *,
        invoice: Invoice,
        days_before_due: int = 2,
    ) -> Reminder | None:
        """
        Ensure an upcoming reminder exists for the next unpaid
        installment of an invoice.

        Args:
            invoice:
                Invoice whose next installment should be reminded.
            days_before_due:
                Number of days before due date to schedule reminder.

        Returns:
            Reminder | None:
                Created reminder or None when no installment qualifies.
        """
        installment = PaymentInstallmentSelector.get_next_due_for_invoice(
            website=invoice.website,
            invoice=invoice,
        )
        if installment is None:
            return None

        if installment.cancelled_at is not None or installment.paid_at is not None:
            return None

        scheduled_for = installment.due_at - timezone.timedelta(
            days=days_before_due
        )

        return cls.schedule_upcoming_installment_reminder(
            invoice=invoice,
            installment=installment,
            scheduled_for=scheduled_for,
        )

    @classmethod
    def ensure_next_installment_due_reminder(
        cls,
        *,
        invoice: Invoice,
    ) -> Reminder | None:
        """
        Ensure a due reminder exists for the next unpaid installment of
        an invoice.

        Args:
            invoice:
                Invoice whose next installment should be reminded.

        Returns:
            Reminder | None:
                Created reminder or None when no installment qualifies.
        """
        installment = PaymentInstallmentSelector.get_next_due_for_invoice(
            website=invoice.website,
            invoice=invoice,
        )
        if installment is None:
            return None

        if installment.cancelled_at is not None or installment.paid_at is not None:
            return None

        return cls.schedule_due_installment_reminder(
            invoice=invoice,
            installment=installment,
            scheduled_for=installment.due_at,
        )
    
    @classmethod
    @transaction.atomic
    def ensure_invoice_reminder(
        cls,
        *,
        invoice: Invoice,
        event_key: str = "billing.invoice.reminder",
        channel: str = "email",
        scheduled_for=None,
        triggered_by=None,
    ) -> Reminder:
        """
        Ensure a pending reminder exists for an invoice.
        """
        cls._validate_receivable_target(invoice=invoice)

        if not cls._is_invoice_remindable(invoice=invoice):
            raise ValidationError(
                "Terminal invoices cannot receive reminders."
            )

        existing = cls._find_existing_pending_reminder(
            website=invoice.website,
            invoice=invoice,
            event_key=event_key,
            scheduled_for=scheduled_for,
        )
        if existing is not None:
            return existing

        reminder = ReminderService.create_reminder(
            website=invoice.website,
            invoice=invoice,
            channel=channel,
            event_key=event_key,
            scheduled_for=scheduled_for,
        )

        AuditLogService.log(
            action="billing.reminder.created",
            actor=triggered_by,
            target=reminder,
            website=invoice.website,
            metadata={
                "event_key": event_key,
                "channel": channel,
                "invoice_id": invoice.pk,
                "invoice_reference": invoice.reference,
            },
        )
        return reminder

    @staticmethod
    def _find_existing_pending_reminder(
        *,
        website,
        invoice: Invoice | None = None,
        payment_request: PaymentRequest | None = None,
        event_key: str,
        scheduled_for,
    ) -> Reminder | None:
        """
        Find an existing pending reminder for an invoice and schedule.

        Args:
            invoice:
                Invoice target.
            event_key:
                Reminder event key.
            scheduled_for:
                Planned dispatch timestamp.

        Returns:
            Reminder | None:
                Existing pending reminder if found, otherwise None.
        """
        queryset = Reminder.objects.filter(
            website=website,
            status=ReminderStatus.PENDING,
            event_key=event_key,
        )

        if invoice is not None:
            queryset = queryset.filter(invoice=invoice)

        if payment_request is not None:
            queryset = queryset.filter(payment_request=payment_request)

        if scheduled_for is None:
            queryset = queryset.filter(scheduled_for__isnull=True)
        else:
            queryset = queryset.filter(scheduled_for=scheduled_for)

        return queryset.first()
    


    @classmethod
    @transaction.atomic
    def ensure_payment_request_reminder(
        cls,
        *,
        payment_request: PaymentRequest,
        event_key: str = "billing.payment_request.reminder",
        channel: str = "email",
        scheduled_for=None,
        triggered_by=None,
    ) -> Reminder:
        """
        Ensure a pending reminder exists for a payment request.
        """
        cls._validate_receivable_target(payment_request=payment_request)

        if not cls._is_payment_request_remindable(
            payment_request=payment_request
        ):
            raise ValidationError(
                "Terminal payment requests cannot receive reminders."
            )

        existing = cls._find_existing_pending_reminder(
            website=payment_request.website,
            payment_request=payment_request,
            event_key=event_key,
            scheduled_for=scheduled_for,
        )
        if existing is not None:
            return existing

        reminder = ReminderService.create_reminder(
            website=payment_request.website,
            payment_request=payment_request,
            channel=channel,
            event_key=event_key,
            scheduled_for=scheduled_for,
        )

        AuditLogService.log(
            action="billing.reminder.created",
            actor=triggered_by,
            target=reminder,
            website=payment_request.website,
            metadata={
                "event_key": event_key,
                "channel": channel,
                "payment_request_id": payment_request.pk,
                "payment_request_reference": payment_request.reference,
            },
        )
        return reminder


    @classmethod
    def ensure_upcoming_installment_reminder(
        cls,
        *,
        invoice: Invoice,
        days_before_due: int = 2,
        channel: str = "email",
        triggered_by=None,
    ) -> Reminder | None:
        """
        Ensure an upcoming reminder exists for the next unpaid
        installment.
        """
        installment = PaymentInstallmentSelector.get_next_due_for_invoice(
            website=invoice.website,
            invoice=invoice,
        )
        if installment is None:
            return None

        if installment.cancelled_at is not None or installment.paid_at is not None:
            return None

        scheduled_for = installment.due_at - timedelta(
            days=days_before_due
        )

        return cls.ensure_invoice_reminder(
            invoice=invoice,
            event_key="billing.installment.upcoming",
            channel=channel,
            scheduled_for=scheduled_for,
            triggered_by=triggered_by,
        )
    


    @classmethod
    def ensure_due_installment_reminder(
        cls,
        *,
        invoice: Invoice,
        channel: str = "email",
        triggered_by=None,
    ) -> Reminder | None:
        """
        Ensure a due reminder exists for the next unpaid installment.
        """
        installment = PaymentInstallmentSelector.get_next_due_for_invoice(
            website=invoice.website,
            invoice=invoice,
        )
        if installment is None:
            return None

        if installment.cancelled_at is not None or installment.paid_at is not None:
            return None

        return cls.ensure_invoice_reminder(
            invoice=invoice,
            event_key="billing.installment.due",
            channel=channel,
            scheduled_for=installment.due_at,
            triggered_by=triggered_by,
        )