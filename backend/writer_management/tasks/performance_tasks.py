"""
writer_management/tasks/performance_tasks.py

Celery tasks for the performance pipeline.

PIPELINE ORDER (weekly, Sunday night → Monday morning)
------------------------------------------------------
Sunday 23:00  run_weekly_aggregation
              → PerformanceAggregatorService.run_weekly()
              → For each writer:
                  WriterMetricsSnapshotService.create_or_update()
                  WriterPerformanceMetrics upserted
              → Percentile ranks computed across all writers

Monday 04:00  run_level_progression
              → LevelProgressionService.evaluate_all()
              → Reads processed snapshots from Sunday
              → Promotes / demotes writers

Monday 06:00  evaluate_weekly_rewards  (reward_tasks.py)
              → Reads WriterPerformanceMetrics from Sunday
              → Awards weekly rewards

The ordering matters:
    aggregation must complete before progression
    progression must complete before rewards
    rewards must complete before the working week starts

CELERY BEAT SCHEDULE (add to settings.py):

    CELERY_BEAT_SCHEDULE = {
        "weekly-performance-aggregation": {
            "task": "writer_management.tasks.performance_tasks"
                    ".run_weekly_aggregation",
            "schedule": crontab(hour=23, minute=0, day_of_week=0),
            # Sunday 23:00 UTC
        },
        "weekly-level-progression": {
            "task": "writer_management.tasks.performance_tasks"
                    ".run_level_progression",
            "schedule": crontab(hour=4, minute=0, day_of_week=1),
            # Monday 04:00 UTC
        },
    }
"""

import logging
from datetime import date, timedelta

from celery import shared_task

logger = logging.getLogger(__name__)


def _last_monday() -> date:
    """Return the most recent Monday (last week's start)."""
    today = date.today()
    return today - timedelta(days=today.weekday() + 7)


@shared_task(
    name="writer_management.tasks.performance_tasks.run_weekly_aggregation",
    bind=True,
    max_retries=2,
    default_retry_delay=600,  # 10 minutes
    time_limit=3600,          # 1 hour hard limit
    soft_time_limit=3300,     # 55 minutes soft limit
)
def run_weekly_aggregation(self, week_start_str: str | None = None):
    """
    Run weekly performance aggregation for all active websites.

    Computes WriterPerformanceSnapshot and WriterPerformanceMetrics
    for all writers on all active sites.

    Args:
        week_start_str: ISO date string 'YYYY-MM-DD'. Defaults to
                        last Monday. Pass explicitly for backfill.
    """
    from websites.models.websites import Website
    from writer_management.services.performance_aggregator_service import (
        PerformanceAggregatorService,
    )

    try:
        if week_start_str:
            week_start = date.fromisoformat(week_start_str)
        else:
            week_start = _last_monday()

        websites = Website.objects.filter(is_active=True)
        total_summary = {
            "week_start": str(week_start),
            "websites":   0,
            "processed":  0,
            "failed":     0,
        }

        for website in websites:
            try:
                summary = PerformanceAggregatorService.run_weekly(
                    website=website,
                    week_start=week_start,
                )
                total_summary["websites"] += 1
                total_summary["processed"] += summary.get("processed", 0)
                total_summary["failed"]    += summary.get("failed", 0)
            except Exception as exc:
                total_summary["failed"] += 1
                logger.exception(
                    "run_weekly_aggregation: website=%s failed: %s",
                    website.pk,
                    exc,
                )

        logger.info(
            "run_weekly_aggregation complete: %s",
            total_summary,
        )
        return total_summary

    except Exception as exc:
        logger.exception("run_weekly_aggregation task failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(
    name="writer_management.tasks.performance_tasks.run_level_progression",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    time_limit=1800,
    soft_time_limit=1500,
)
def run_level_progression(self):
    """
    Evaluate all writers for promotion and demotion.

    Runs after run_weekly_aggregation completes.
    Reads processed WriterPerformanceSnapshots and
    WriterLevelCriteria to determine level changes.
    """
    from websites.models.websites import Website
    from writer_management.services.level_progression_service import (
        LevelProgressionService,
    )

    try:
        websites = Website.objects.filter(is_active=True)
        total_summary = {
            "websites":  0,
            "evaluated": 0,
            "promoted":  0,
            "demoted":   0,
            "unchanged": 0,
            "errors":    0,
        }

        for website in websites:
            try:
                summary = LevelProgressionService.evaluate_all(
                    website=website,
                )
                total_summary["websites"]  += 1
                for key in ("evaluated", "promoted", "demoted",
                            "unchanged", "errors"):
                    total_summary[key] += summary.get(key, 0)
            except Exception as exc:
                logger.exception(
                    "run_level_progression: website=%s failed: %s",
                    website.pk,
                    exc,
                )

        logger.info(
            "run_level_progression complete: %s",
            total_summary,
        )
        return total_summary

    except Exception as exc:
        logger.exception("run_level_progression task failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(
    name="writer_management.tasks.performance_tasks.backfill_writer_metrics",
    bind=True,
    max_retries=1,
)
def backfill_writer_metrics(
    self,
    writer_registration_id: str,
    week_start_str: str,
):
    """
    Backfill metrics for a single writer for a specific week.

    Args:
        writer_registration_id: WriterProfile.registration_id.
        week_start_str:         ISO date 'YYYY-MM-DD' (must be a Monday).
    """
    from writer_management.models.writer_profile import WriterProfile
    from writer_management.services.performance_aggregator_service import (
        PerformanceAggregatorService,
    )

    try:
        writer_profile = WriterProfile.objects.select_related(
            "writer_level",
            "writer_level__website",
        ).get(registration_id=writer_registration_id)

        # Guard — writer_level is nullable
        if writer_profile.writer_level is None:
            logger.error(
                "backfill_writer_metrics: writer=%s has no level assigned. "
                "Cannot resolve website. Assign a level first.",
                writer_registration_id,
            )
            return {
                "status": "no_level",
                "writer": writer_registration_id,
            }

        website = writer_profile.writer_level.website
        week_start = date.fromisoformat(week_start_str)

        PerformanceAggregatorService.run_for_writer(
            writer_profile=writer_profile,
            website=website,
            week_start=week_start,
        )

        logger.info(
            "backfill_writer_metrics: writer=%s week=%s complete.",
            writer_registration_id,
            week_start_str,
        )
        return {"status": "complete", "writer": writer_registration_id}

    except WriterProfile.DoesNotExist:
        logger.error(
            "backfill_writer_metrics: writer=%s not found.",
            writer_registration_id,
        )
        return {"status": "not_found", "writer": writer_registration_id}

    except Exception as exc:
        logger.exception(
            "backfill_writer_metrics: writer=%s failed: %s",
            writer_registration_id,
            exc,
        )
        raise self.retry(exc=exc)