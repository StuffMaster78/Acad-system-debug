from __future__ import annotations

from django.utils import timezone

from class_management.selectors.class_access_selectors import (
    ClassAccessSelector,
)
from notifications_system.services.notification_service import (
    NotificationService,
)


def send_two_factor_reminders():
    """
    Notify client when 2FA is requested.
    """
    requests = ClassAccessSelector.pending_two_factor_requests(
        website=None,
    )

    now = timezone.now()

    for req in requests:
        if req.needed_by and req.needed_by <= now:
            NotificationService.notify(
                event_key="class.two_factor.required",
                recipient=req.class_order.client,
                website=req.class_order.website,
                context={
                    "class_order_id": req.class_order.id,
                    "request_notes": req.request_notes,
                },
                triggered_by=req.requested_by,
            )