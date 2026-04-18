from datetime import datetime, timedelta
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.services.dispute_enums import DisputeStatus

User = get_user_model()


def validate_dispute_status_transition(
    current_status: str,
    new_status: str,
) -> None:
    """
    Validate whether a dispute can move to a new status.

    Args:
        current_status: Current dispute status.
        new_status: Proposed next status.

    Raises:
        ValidationError: If the transition is not allowed.
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
            f"Cannot transition dispute from {current_status} to "
            f"{new_status}."
        )


def send_dispute_notification(
    dispute,
    event_key: str,
    message: str,
    triggered_by=None,
) -> None:
    """
    Send dispute notifications through NotificationService.

    Recipients:
    1. Assigned writer, if any
    2. User who raised the dispute
    3. Staff users with admin, support, or superadmin role
    4. Website admin users
    """
    website = dispute.website
    recipients = {}

    writer = getattr(dispute.order, "assigned_writer", None)
    if writer:
        recipients[writer.id] = writer

    if dispute.raised_by:
        recipients[dispute.raised_by.id] = dispute.raised_by

    staff_users = User.objects.filter(
        role__in=["admin", "support", "superadmin"],
        is_active=True,
    )

    for user in staff_users:
        recipients[user.id] = user

    website_admins = website.get_admin_users()
    for admin in website_admins:
        recipients[admin.id] = admin

    context = {
        "dispute_id": dispute.id,
        "order_id": dispute.order.id if dispute.order else None,
        "status": dispute.status,
        "message": message,
        "website_id": website.id if website else None,
    }

    for recipient in recipients.values():
        try:
            NotificationService.notify(
                event_key=event_key,
                recipient=recipient,
                website=website,
                context=context,
                channels=["email", "in_app"],
                triggered_by=triggered_by,
                priority="high",
                is_broadcast=False,
                is_critical=False,
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )
        except Exception:
            continue


def calculate_extended_deadline(
    current_deadline: Optional[datetime],
    extension_days: int,
) -> datetime:
    """
    Calculate a new deadline based on an extension.

    Args:
        current_deadline: The original deadline.
        extension_days: Number of days to extend.

    Returns:
        New extended deadline.

    Raises:
        ValidationError: If current deadline is not set.
    """
    if not current_deadline:
        raise ValidationError("Current deadline is not set.")

    return current_deadline + timedelta(days=extension_days)