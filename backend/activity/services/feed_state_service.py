from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from activity.models import ActivityEvent
from activity.models import ActivityFeedState


class ActivityFeedStateService:
    """
    Handles per user feed state changes.
    """

    @staticmethod
    @transaction.atomic
    def ensure_state_for_user(
        *,
        event: ActivityEvent,
        user,
    ) -> ActivityFeedState:
        """
        Ensure a feed state row exists for a user and event.
        """
        state, _created = ActivityFeedState.objects.get_or_create(
            event=event,
            user=user,
        )

        return state

    @staticmethod
    @transaction.atomic
    def mark_read(
        *,
        event: ActivityEvent,
        user,
    ) -> ActivityFeedState:
        """
        Mark an activity event as read for a user.
        """
        state = ActivityFeedStateService.ensure_state_for_user(
            event=event,
            user=user,
        )

        if state.is_read:
            return state

        state.is_read = True
        state.read_at = timezone.now()
        state.save(update_fields=["is_read", "read_at"])

        return state
    
    @staticmethod
    @transaction.atomic
    def bulk_mark_read(
        *,
        events: list[ActivityEvent],
        user,
    ) -> int:
        """
        Mark many activity events as read for a user.

        Returns:
            Number of feed state rows affected.
        """
        affected = 0

        for event in events:
            state = ActivityFeedStateService.mark_read(
                event=event,
                user=user,
            )

            if state.is_read:
                affected += 1

        return affected

    @staticmethod
    @transaction.atomic
    def mark_unread(
        *,
        event: ActivityEvent,
        user,
    ) -> ActivityFeedState:
        """
        Mark an activity event as unread for a user.
        """
        state = ActivityFeedStateService.ensure_state_for_user(
            event=event,
            user=user,
        )

        if not state.is_read:
            return state

        state.is_read = False
        state.read_at = None
        state.save(update_fields=["is_read", "read_at"])

        return state

    @staticmethod
    @transaction.atomic
    def dismiss(
        *,
        event: ActivityEvent,
        user,
    ) -> ActivityFeedState:
        """
        Dismiss an activity event for a user.
        """
        state = ActivityFeedStateService.ensure_state_for_user(
            event=event,
            user=user,
        )

        if state.is_dismissed:
            return state

        state.is_dismissed = True
        state.dismissed_at = timezone.now()
        state.save(update_fields=["is_dismissed", "dismissed_at"])

        return state
    
    @staticmethod
    @transaction.atomic
    def restore(
        *,
        event: ActivityEvent,
        user,
    ) -> ActivityFeedState:
        """
        Restore a dismissed activity event for a user.
        """
        state = ActivityFeedStateService.ensure_state_for_user(
            event=event,
            user=user,
        )

        if not state.is_dismissed:
            return state

        state.is_dismissed = False
        state.dismissed_at = None
        state.save(update_fields=["is_dismissed", "dismissed_at"])

        return state

    @staticmethod
    @transaction.atomic
    def pin(
        *,
        event: ActivityEvent,
        user,
    ) -> ActivityFeedState:
        """
        Pin an activity event for a user.
        """
        state = ActivityFeedStateService.ensure_state_for_user(
            event=event,
            user=user,
        )

        if state.is_pinned:
            return state

        state.is_pinned = True
        state.save(update_fields=["is_pinned"])

        return state

    @staticmethod
    @transaction.atomic
    def unpin(
        *,
        event: ActivityEvent,
        user,
    ) -> ActivityFeedState:
        """
        Unpin an activity event for a user.
        """
        state = ActivityFeedStateService.ensure_state_for_user(
            event=event,
            user=user,
        )

        if not state.is_pinned:
            return state

        state.is_pinned = False
        state.save(update_fields=["is_pinned"])

        return state