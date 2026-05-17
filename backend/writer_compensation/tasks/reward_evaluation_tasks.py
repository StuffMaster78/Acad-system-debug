from __future__ import annotations

from celery import shared_task
from django.utils import timezone

from websites.models.websites import Website
from writer_management.models.writer_profile import (
    WriterProfile,
)
from writer_compensation.services.reward_evaluation_service import (
    RewardEvaluationService,
)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def evaluate_weekly_writer_rewards(
    self,
    *,
    website_id: int,
) -> dict:
    """
    Weekly reward evaluation task.

    Intended schedule:
        every Sunday night
        or Monday morning UTC.

    Evaluates:
        - weekly bonuses
        - leaderboard rewards
        - retention incentives
    """

    website = Website.objects.get(
        pk=website_id,
    )

    writers = (
        WriterProfile.objects
        .filter(
            is_deleted=False,
            onboarding_status="COMPLETED",
        )
        .select_related(
            "writer_level",
        )
    )

    now = timezone.now().date()

    period_end = now
    period_start = (
        now - timezone.timedelta(days=7)
    )

    rewards = (
        RewardEvaluationService
        .evaluate_many_writers(
            website=website,
            writers=writers,
            period_start=period_start,
            period_end=period_end,
        )
    )

    return {
        "website_id": website.pk,
        "evaluated_writers": writers.count(),
        "issued_rewards": len(rewards),
        "period_start": str(period_start),
        "period_end": str(period_end),
    }


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def evaluate_monthly_writer_rewards(
    self,
    *,
    website_id: int,
) -> dict:
    """
    Monthly reward evaluation task.

    Intended schedule:
        first day of month.
    """

    website = Website.objects.get(
        pk=website_id,
    )

    writers = (
        WriterProfile.objects
        .filter(
            is_deleted=False,
            onboarding_status="COMPLETED",
        )
        .select_related(
            "writer_level",
        )
    )

    now = timezone.now().date()

    period_end = now
    period_start = (
        now - timezone.timedelta(days=30)
    )

    rewards = (
        RewardEvaluationService
        .evaluate_many_writers(
            website=website,
            writers=writers,
            period_start=period_start,
            period_end=period_end,
        )
    )

    return {
        "website_id": website.pk,
        "evaluated_writers": writers.count(),
        "issued_rewards": len(rewards),
        "period_start": str(period_start),
        "period_end": str(period_end),
    }