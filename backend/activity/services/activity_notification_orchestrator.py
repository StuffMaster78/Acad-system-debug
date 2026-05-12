from __future__ import annotations

from typing import Iterable, Set, TYPE_CHECKING

from django.contrib.auth import get_user_model

from activity.constants import ActivityAudience
from activity.integrations.notification_integration import (
    ActivityNotificationIntegration,
)
from activity.models import ActivityEvent


if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser as User
else:
    User = get_user_model()

class ActivityNotificationOrchestrator:
    """
    Orchestrates notification dispatch from activity events.
    """

    NOTIFIABLE_VERBS = {
        "order.assigned",
        "order.completed",
        "payment.failed",
        "payment.succeeded",
    }

    @staticmethod
    def handle_event(*, event: ActivityEvent) -> None:
        """
        Decide whether and how to notify users for an event.
        """
        # Gate first (cheap check)
        if event.verb not in ActivityNotificationOrchestrator.NOTIFIABLE_VERBS:
            return

        recipients = ActivityNotificationOrchestrator._resolve_recipients(
            event=event,
        )

        if not recipients:
            return

        for user in recipients:
            try:
                ActivityNotificationIntegration.notify_from_event(
                    event=event,
                    recipient=user,
                )
            except Exception:
                # Never let notifications break flow
                continue

    @staticmethod
    def _resolve_recipients(
        *,
        event: ActivityEvent,
    ) -> Iterable[User]:
        """
        Determine which users should receive notifications.
        """
        recipients: Set[User] = set()

        target = event.target

        # --- Target-based resolution ---

        if target is not None:
            if hasattr(target, "client") and target.client:
                recipients.add(target.client)

            if hasattr(target, "assigned_to") and target.assigned_to:
                recipients.add(target.assigned_to)

        # --- Actor exclusion ---
        if event.actor:
            recipients.discard(event.actor)

        # --- Audience filtering ---
        recipients = {
            user
            for user in recipients
            if ActivityNotificationOrchestrator._allowed_by_audience(
                user=user,
                audiences=event.audiences,
            )
        }

        return recipients

    @staticmethod
    def _allowed_by_audience(
        *,
        user: User,
        audiences: Iterable[str],
    ) -> bool:
        """
        Check whether a user is allowed based on event audiences.
        """
        if not audiences:
            return False

        if user.is_staff and ActivityAudience.STAFF in audiences:
            return True

        if not user.is_staff and ActivityAudience.CLIENT in audiences:
            return True

        return False