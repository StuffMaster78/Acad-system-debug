from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from activity.models import ActivityFeedState


@shared_task
def cleanup_dismissed_feed_states(days: int = 90) -> int:
    """
    Delete old dismissed feed states.

    Canonical activity events are retained. This only cleans user specific
    feed state rows.
    """
    cutoff = timezone.now() - timedelta(days=days)

    deleted_count, _details = ActivityFeedState.objects.filter(
        is_dismissed=True,
        dismissed_at__lt=cutoff,
    ).delete()

    return deleted_count