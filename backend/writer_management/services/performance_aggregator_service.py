"""
writer_management/services/performance_aggregator_service.py

Coordinates the weekly metrics pipeline across all writers on a site.

PIPELINE
--------
Step 1: For each writer on the site, call
        WriterMetricsSnapshotService.create_or_update()
        → creates/updates WriterPerformanceSnapshot (processed)
        → creates/updates WriterPerformanceMetrics (weekly row)

Step 2: After all writers are processed, compute percentile ranks
        by comparing each writer's composite score against all
        other writers on the same site for the same week.

Step 3: Write percentile_rank back to each WriterPerformanceMetrics row.

ENTRY POINTS
------------
run_weekly(website, week_start)
    Called by Celery Beat every Sunday night / Monday morning.
    Processes all active writers on the site.

run_for_writer(writer_profile, website, week_start)
    Process a single writer. Used for ad-hoc backfill and testing.

CALLED BY
---------
Celery task: writer_management.tasks.performance_tasks.run_weekly_aggregation
"""

import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction

from writer_management.services.composite_score_service import (
    CompositeScoreService,
)
from writer_management.services.writer_metrics_snapshot_service import (
    WriterMetricsSnapshotService,
)

logger = logging.getLogger(__name__)


class PerformanceAggregatorService:

    @staticmethod
    def run_weekly(website, week_start: date) -> dict:
        """
        Run the full weekly performance pipeline for a website.

        Args:
            website:    Website instance.
            week_start: Monday of the week to process.

        Returns:
            Summary dict: {processed, failed, total}
        """
        week_end = week_start + timedelta(days=6)

        writers = PerformanceAggregatorService._get_active_writers(website)
        total = writers.count()
        processed = 0
        failed = 0

        logger.info(
            "PerformanceAggregator.run_weekly: website=%s "
            "week=%s→%s writers=%d",
            website.pk, week_start, week_end, total,
        )

        # Step 1 — Snapshots and weekly metrics
        for writer_profile in writers.iterator(chunk_size=100):
            try:
                PerformanceAggregatorService.run_for_writer(
                    writer_profile=writer_profile,
                    website=website,
                    week_start=week_start,
                    week_end=week_end,
                )
                processed += 1
            except Exception as exc:
                failed += 1
                logger.exception(
                    "PerformanceAggregator: failed for writer=%s: %s",
                    writer_profile.registration_id,
                    exc,
                )

        # Step 2 — Percentile ranks across all writers this week
        PerformanceAggregatorService._compute_percentile_ranks(
            website=website,
            week_start=week_start,
        )

        summary = {
            "week_start": str(week_start),
            "week_end":   str(week_end),
            "total":      total,
            "processed":  processed,
            "failed":     failed,
        }
        logger.info("PerformanceAggregator.run_weekly complete: %s", summary)
        return summary

    @staticmethod
    @transaction.atomic
    def run_for_writer(
        writer_profile,
        website,
        week_start: date,
        week_end: date | None = None,
    ) -> None:
        """
        Process a single writer for a week.

        1. Create/update WriterPerformanceSnapshot (monthly view)
        2. Create/update WriterPerformanceMetrics (weekly view)

        Args:
            writer_profile: WriterProfile instance.
            website:        Website instance.
            week_start:     Monday of the week.
            week_end:       Sunday of the week. Computed if not provided.
        """
        if week_end is None:
            week_end = week_start + timedelta(days=6)

        # Step 1 — Snapshot (also computes composite_score)
        snapshot = WriterMetricsSnapshotService.create_or_update(
            writer_profile=writer_profile,
            website=website,
            period_start=week_start,
            period_end=week_end,
        )

        # Step 2 — Weekly metrics row
        PerformanceAggregatorService._upsert_weekly_metrics(
            writer_profile=writer_profile,
            website=website,
            week_start=week_start,
            week_end=week_end,
            snapshot=snapshot,
        )

    @staticmethod
    def _upsert_weekly_metrics(
        writer_profile,
        website,
        week_start: date,
        week_end: date,
        snapshot,
    ) -> None:
        """
        Create or update WriterPerformanceMetrics for a week.
        Pulls values from the processed snapshot.
        """
        from writer_management.models.writer_performance import WriterPerformanceMetrics

        # Convert proportion rates to percentages for metrics display
        def pct(proportion) -> Decimal:
            if proportion is None:
                return Decimal("0.00")
            return (Decimal(str(proportion)) * 100).quantize(Decimal("0.01"))

        WriterPerformanceMetrics.objects.update_or_create(
            writer=writer_profile,
            website=website,
            week_start=week_start,
            defaults={
                "week_end":                     week_end,
                "avg_rating":                   snapshot.average_rating or Decimal("0.00"),
                "revision_rate":                pct(snapshot.revision_rate),
                "dispute_rate":                 pct(snapshot.dispute_rate),
                "lateness_rate":                pct(snapshot.lateness_rate),
                "cancellation_rate":            pct(snapshot.cancellation_rate),
                "acceptance_to_completion_ratio": pct(snapshot.completion_rate),
                "preferred_order_rate":         pct(snapshot.preferred_order_rate),
                "avg_turnaround_time":          None,  # DurationField — set separately
                "total_orders_completed":       snapshot.completed_orders,
                "total_pages_completed":        snapshot.total_pages,
                "hvo_orders_completed":         snapshot.hvo_orders,
                "total_earnings":               snapshot.amount_paid,
                "total_tips":                   snapshot.tips,
                "total_bonuses":                snapshot.bonuses,
                "total_fines":                  Decimal("0.00"),
                "total_profit_contribution":    snapshot.profit_contribution,
                "composite_score":              snapshot.composite_score or Decimal("0.00"),
                # percentile_rank written in Step 2 of run_weekly
                "percentile_rank":              Decimal("0.00"),
            },
        )

    @staticmethod
    def _compute_percentile_ranks(website, week_start: date) -> None:
        """
        Compute percentile rank for every writer on a site for a week.

        Percentile rank = % of writers this writer outperforms.

        Runs after all individual writer metrics have been written.
        Updates percentile_rank in bulk.
        """
        from writer_management.models.writer_performance import WriterPerformanceMetrics

        metrics_qs = WriterPerformanceMetrics.objects.filter(
            website=website,
            week_start=week_start,
        ).values_list("pk", "composite_score")

        rows = list(metrics_qs)
        if not rows:
            return

        all_scores = [Decimal(str(score)) for _, score in rows]

        # Compute and bulk update
        updates = []
        for pk, composite_score in rows:
            score = Decimal(str(composite_score))
            percentile = CompositeScoreService.compute_percentile(
                writer_score=score,
                all_scores=all_scores,
            )
            updates.append(
                WriterPerformanceMetrics(pk=pk, percentile_rank=percentile)
            )

        WriterPerformanceMetrics.objects.bulk_update(
            updates,
            ["percentile_rank"],
        )

        logger.info(
            "_compute_percentile_ranks: website=%s week=%s writers=%d",
            website.pk,
            week_start,
            len(rows),
        )

    @staticmethod
    def _get_active_writers(website):
        """Return active, non-deleted writers for a website."""
        from writer_management.models.writer_profile import WriterProfile

        return WriterProfile.objects.filter(
            writer_level__website=website,
            is_deleted=False,
            onboarding_status="completed",
        ).select_related(
            "writer_level",
            "capacity",
        )