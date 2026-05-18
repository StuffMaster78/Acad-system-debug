from __future__ import annotations

from celery import shared_task

from websites.models.websites import Website
from writer_compensation.services.reward_analytics_snapshot_service import (
    RewardAnalyticsSnapshotService,
)


@shared_task(
    bind=True,
    max_retries=3,
)
def generate_reward_analytics_snapshots(
    self,
) -> None:
    """
    Generate daily analytics snapshots.
    """

    websites = Website.objects.all()

    for website in websites:
        RewardAnalyticsSnapshotService(
        ).generate_daily_snapshot(
            website=website,
        )