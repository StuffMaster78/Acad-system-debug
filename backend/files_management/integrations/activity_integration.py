from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def handle_file_first_downloaded(sender, *, attachment, user, **kwargs) -> None:
    """
    Record an activity event when a client downloads a final file for the
    first time. Connected to the file_first_downloaded signal.

    Only fires for guarded purposes (ORDER_FINAL, special order milestones)
    to keep the activity feed signal-to-noise ratio high.
    """
    try:
        from activity.constants import (
            ActivityAudience,
            ActivitySeverity,
            ActivityVerb,
        )
        from activity.services.activity_service import ActivityService
        from files_management.services.file_delivery_guard_service import (
            GUARDED_PURPOSES,
        )

        if attachment.purpose not in GUARDED_PURPOSES:
            return

        order = getattr(attachment, "content_object", None)
        if order is None:
            return

        website = getattr(order, "website", None)
        if website is None:
            return

        ActivityService.record_event(
            website=website,
            verb=ActivityVerb.FILE_DOWNLOADED,
            actor=user,
            target=order,
            audiences=[ActivityAudience.CLIENT, ActivityAudience.STAFF],
            severity=ActivitySeverity.INFO,
            title="Final file downloaded",
            summary=(
                f"Client downloaded the final delivery for "
                f"order #{getattr(order, 'pk', '?')}"
            ),
            metadata={
                "attachment_id": attachment.pk,
                "order_id": getattr(order, "pk", None),
                "purpose": attachment.purpose,
            },
        )
    except Exception as exc:
        log.warning(
            "handle_file_first_downloaded: activity event failed "
            "attachment=%s: %s",
            getattr(attachment, "pk", None),
            exc,
        )
