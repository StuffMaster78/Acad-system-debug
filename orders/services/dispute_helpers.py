from datetime import datetime, timedelta
from typing import Optional, List

from django.core.exceptions import ValidationError
from django.utils import timezone

from users.models import User
from orders.services.dispute_enums import DisputeStatus
from notifications_system.utils import send_website_mail


def validate_dispute_status_transition(
    current_status: str, new_status: str
) -> None:
    """
    Validate if a dispute can transition from current to new status.

    Args:
        current_status (str): Current dispute status as string.
        new_status (str): Proposed new status as string.

    Raises:
        ValidationError: If transition is not allowed.
    """
    allowed_transitions = {
        DisputeStatus.OPEN.value: [
            DisputeStatus.IN_REVIEW.value,
            DisputeStatus.ESCALATED.value,
            DisputeStatus.RESOLVED.value,
        ],
        DisputeStatus.IN_REVIEW.value: [
            DisputeStatus.ESCALATED.value,
            DisputeStatus.RESOLVED.value,
        ],
        DisputeStatus.ESCALATED.value: [
            DisputeStatus.RESOLVED.value,
        ],
        DisputeStatus.RESOLVED.value: [],
    }

    if new_status not in allowed_transitions.get(current_status, []):
        raise ValidationError(
            f"Cannot transition dispute from {current_status} to {new_status}."
        )


def send_dispute_notification(
    dispute,
    subject: str,
    message: str,
    extra_recipients: Optional[List[str]] = None,
) -> None:
    """
    Send email notifications related to a dispute.

    Args:
        dispute (Dispute): Dispute instance.
        subject (str): Email subject.
        message (str): Email message.
        extra_recipients (list[str], optional): Extra email addresses.
    """
    website = dispute.website
    recipients = set(extra_recipients or [])

    # Include writer
    if dispute.order.writer and dispute.order.writer.email:
        recipients.add(dispute.order.writer.email)

    # Include client who raised the dispute
    if dispute.raised_by and dispute.raised_by.email:
        recipients.add(dispute.raised_by.email)

    # Include staff (admin, support, superadmin)
    staff_emails = User.objects.filter(
        role__in=["admin", "support", "superadmin"]
    ).values_list("email", flat=True)

    recipients.update(staff_emails)

    # Send to all collected recipients
    if recipients:
        send_website_mail(
            website=website,
            subject=subject,
            message=message,
            recipient_list=list(recipients),
        )

    # Also send directly to all admins associated with the website
    website_admins = website.get_admin_users()
    admin_emails = [admin.email for admin in website_admins]

    if admin_emails:
        send_website_mail(
            website=website,
            subject=subject,
            message=message,
            recipient_list=admin_emails,
        )


def calculate_extended_deadline(
    current_deadline: Optional[datetime],
    extension_days: int
) -> datetime:
    """
    Calculate a new deadline based on an extension.

    Args:
        current_deadline (datetime): The original deadline.
        extension_days (int): Number of days to extend.

    Returns:
        datetime: New extended deadline.

    Raises:
        ValidationError: If current deadline is not set.
    """
    if not current_deadline:
        raise ValidationError("Current deadline is not set.")

    return current_deadline + timedelta(days=extension_days)