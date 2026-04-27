from __future__ import annotations

from celery import shared_task
from django.utils import timezone
from billing.models.reminder import Reminder
from billing.models.invoice import Invoice
from billing.selectors.invoice_selectors import InvoiceSelector
from billing.selectors.reminder_selectors import ReminderSelector
from billing.services.reminder_orchestration_service import (
    ReminderOrchestrationService,
)
from billing.selectors.payment_installment_selectors import (
    PaymentInstallmentSelector,
)
from billing.constants import InvoiceStatus, ReminderStatus


@shared_task
def schedule_upcoming_installment_reminders() -> int:
    """
    Schedule upcoming installment reminders across all active invoices.

    Returns:
        int:
            Number of reminders created.
    """
    count = 0

    invoices = Invoice.objects.filter(status__in=["issued", "partially_paid"])

    for invoice in invoices:
        installments = (
            PaymentInstallmentSelector.get_upcoming_queryset_for_invoice(
                website=invoice.website,
                invoice=invoice,
                days_ahead=2,
            )
        )

        for installment in installments:
            scheduled_for = installment.due_at

            existing = (
                ReminderOrchestrationService
                ._find_existing_pending_reminder(
                    website=invoice.website,
                    invoice=invoice,
                    event_key="billing.installment.upcoming",
                    scheduled_for=scheduled_for,
                )
            )
            if existing is not None:
                continue

            ReminderOrchestrationService.schedule_upcoming_installment_reminder(
                invoice=invoice,
                installment=installment,
                scheduled_for=scheduled_for,
            )
            count += 1

    return count


@shared_task
def schedule_due_installment_reminders() -> int:
    """
    Schedule due reminders across invoices with overdue installments.

    Returns:
        int:
            Number of reminders created.
    """
    count = 0

    invoices = Invoice.objects.filter(status__in=[
        InvoiceStatus.ISSUED,
        InvoiceStatus.PARTIALLY_PAID,
    ])

    for invoice in invoices:
        installments = (
            PaymentInstallmentSelector.get_overdue_queryset_for_invoice(
                website=invoice.website,
                invoice=invoice,
            )
        )

        for installment in installments:
            scheduled_for = installment.due_at

            existing = (
                ReminderOrchestrationService
                ._find_existing_pending_reminder(
                    website=invoice.website,
                    invoice=invoice,
                    event_key="billing.installment.due",
                    scheduled_for=scheduled_for,
                )
            )
            if existing is not None:
                continue

            ReminderOrchestrationService.schedule_due_installment_reminder(
                invoice=invoice,
                installment=installment,
                scheduled_for=scheduled_for,
            )
            count += 1

    return count


@shared_task
def dispatch_due_billing_reminders() -> int:
    """
    Dispatch all billing reminders that are due now.

    Returns:
        int:
            Number of reminders processed.
    """
    count = 0

    reminders = Reminder.objects.filter(
        status=ReminderStatus.PENDING,
        scheduled_for__isnull=False,
        scheduled_for__lte=timezone.now(),
    ).order_by("scheduled_for", "created_at")

    for reminder in reminders:
        ReminderOrchestrationService.dispatch_reminder(
            reminder=reminder,
            triggered_by=None,
        )
        count += 1

    return count