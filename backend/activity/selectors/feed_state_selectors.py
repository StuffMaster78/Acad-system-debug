from __future__ import annotations

from django.db.models import QuerySet

from activity.models import ActivityFeedState


class ActivityFeedStateSelector:
    """
    Read helpers for activity feed state.
    """

    @staticmethod
    def for_user(*, user) -> QuerySet[ActivityFeedState]:
        """
        Return feed states for a user.
        """
        return ActivityFeedState.objects.filter(
            user=user,
        ).select_related(
            "event",
        )

    @staticmethod
    def unread_for_user(*, user) -> QuerySet[ActivityFeedState]:
        """
        Return unread feed states for a user.
        """
        return ActivityFeedStateSelector.for_user(
            user=user,
        ).filter(
            is_read=False,
            is_dismissed=False,
        )

    @staticmethod
    def pinned_for_user(*, user) -> QuerySet[ActivityFeedState]:
        """
        Return pinned feed states for a user.
        """
        return ActivityFeedStateSelector.for_user(
            user=user,
        ).filter(
            is_pinned=True,
            is_dismissed=False,
        )