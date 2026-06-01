"""
writer_management/tasks/reward_tasks.py

Celery tasks for reward evaluation.

SCHEDULE (add to settings.py CELERY_BEAT_SCHEDULE):

    "evaluate-weekly-rewards": {
        "task": "writer_management.tasks.reward_tasks.evaluate_weekly_rewards",
        "schedule": crontab(hour=6, minute=0, day_of_week=1),
        # Every Monday at 06:00 — after weekly metrics are computed
    },
    "evaluate-monthly-rewards": {
        "task": "writer_management.tasks.reward_tasks.evaluate_monthly_rewards",
        "schedule": crontab(hour=7, minute=0, day_of_month=1),
        # First day of each month at 07:00
    },
    "evaluate-lifetime-rewards": {
        "task": "writer_management.tasks.reward_tasks.evaluate_lifetime_rewards",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),
        # Weekly check for newly qualifying lifetime rewards
    },

ORDERING NOTE
-------------
Weekly rewards must run AFTER weekly metrics are computed.
performance_aggregator_service task should run Sunday night.
evaluate_weekly_rewards runs Monday morning.

If metrics are not yet computed when this task runs,
_candidates_weekly returns an empty queryset and no rewards
are granted. The task is safe to re-run manually.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="writer_management.tasks.reward_tasks.evaluate_weekly_rewards",
    bind=True,
    max_retries=2,
    default_retry_delay=300, # 5 minutes
)
def evaluate_weekly_rewards(self):
    """
    Evaluate all weekly WriterRewardCriteria across all active websites.

    Run every Monday morning after weekly metrics are computed.
    Safe to re-run — idempotent per writer per period.
    """
    from websites.models.websites import Website
    from writer_management.services.reward_evaluation_service import (
        RewardEvaluationService,
    )

    try:
        websites = Website.objects.filter(is_active=True)
        total_summary = {
            "websites": 0,
            "evaluated": 0,
            "granted": 0,
            "skipped": 0,
            "errors": 0,
        }

        for website in websites:
            # Only evaluate weekly criteria
            from writer_management.models.writer_reward import WriterRewardCriteria
            has_weekly = WriterRewardCriteria.objects.filter(
                website=website,
                is_active=True,
                evaluation_period="weekly",
            ).exists()

            if not has_weekly:
                continue

            summary = RewardEvaluationService.evaluate_all(website)
            total_summary["websites"] += 1
            for key in ("evaluated", "granted", "skipped", "errors"):
                total_summary[key] += summary.get(key, 0)

        logger.info(
            "evaluate_weekly_rewards complete: %s",
            total_summary,
        )
        return total_summary

    except Exception as exc:
        logger.exception("evaluate_weekly_rewards failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(
    name="writer_management.tasks.reward_tasks.evaluate_monthly_rewards",
    bind=True,
    max_retries=2,
    default_retry_delay=600, # 10 minutes
)
def evaluate_monthly_rewards(self):
    """
    Evaluate all monthly WriterRewardCriteria across all active websites.

    Run on the first day of each month after monthly snapshots
    are computed.
    """
    from websites.models.websites import Website
    from writer_management.services.reward_evaluation_service import (
        RewardEvaluationService,
    )

    try:
        websites = Website.objects.filter(is_active=True)
        total_summary = {
            "websites": 0,
            "evaluated": 0,
            "granted": 0,
            "skipped": 0,
            "errors": 0,
        }

        for website in websites:
            from writer_management.models.writer_reward import WriterRewardCriteria
            has_monthly = WriterRewardCriteria.objects.filter(
                website=website,
                is_active=True,
                evaluation_period="monthly",
            ).exists()

            if not has_monthly:
                continue

            summary = RewardEvaluationService.evaluate_all(website)
            total_summary["websites"] += 1
            for key in ("evaluated", "granted", "skipped", "errors"):
                total_summary[key] += summary.get(key, 0)

        logger.info(
            "evaluate_monthly_rewards complete: %s",
            total_summary,
        )
        return total_summary

    except Exception as exc:
        logger.exception("evaluate_monthly_rewards failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(
    name="writer_management.tasks.reward_tasks.evaluate_lifetime_rewards",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
)
def evaluate_lifetime_rewards(self):
    """
    Evaluate lifetime WriterRewardCriteria.

    Run weekly — writers cross lifetime thresholds infrequently
    but the check is cheap (lifetime totals are always up to date).

    Idempotency: lifetime rewards are one-time only.
    _already_awarded() prevents duplicate grants.
    """
    from websites.models.websites import Website
    from writer_management.services.reward_evaluation_service import (
        RewardEvaluationService,
    )

    try:
        websites = Website.objects.filter(is_active=True)
        total_summary = {
            "websites": 0,
            "evaluated": 0,
            "granted": 0,
            "skipped": 0,
            "errors": 0,
        }

        for website in websites:
            from writer_management.models.writer_reward import WriterRewardCriteria
            has_lifetime = WriterRewardCriteria.objects.filter(
                website=website,
                is_active=True,
                evaluation_period="lifetime",
            ).exists()

            if not has_lifetime:
                continue

            summary = RewardEvaluationService.evaluate_all(website)
            total_summary["websites"] += 1
            for key in ("evaluated", "granted", "skipped", "errors"):
                total_summary[key] += summary.get(key, 0)

        logger.info(
            "evaluate_lifetime_rewards complete: %s",
            total_summary,
        )
        return total_summary

    except Exception as exc:
        logger.exception("evaluate_lifetime_rewards failed: %s", exc)
        raise self.retry(exc=exc)



# from __future__ import annotations

# import logging

# from celery import shared_task

# from writer_compensation.services.reward_evaluation_orchestrator import (
# RewardEvaluationOrchestrator,
# )

# logger = logging.getLogger(__name__)


# @shared_task(
# bind=True,
# autoretry_for=(Exception,),
# retry_backoff=True,
# retry_jitter=True,
# max_retries=3,
# )
# def run_weekly_rewards_task(self) -> None:
# """
# Execute weekly reward cycle.
# """

# logger.info(
# "Starting weekly reward evaluation task.",
# )

# RewardEvaluationOrchestrator.run_weekly_rewards()

# logger.info(
# "Completed weekly reward evaluation task.",
# )


# @shared_task(
# bind=True,
# autoretry_for=(Exception,),
# retry_backoff=True,
# retry_jitter=True,
# max_retries=3,
# )
# def run_monthly_rewards_task(self) -> None:
# """
# Execute monthly reward cycle.
# """

# logger.info(
# "Starting monthly reward evaluation task.",
# )

# RewardEvaluationOrchestrator.run_monthly_rewards()

# logger.info(
# "Completed monthly reward evaluation task.",
# )