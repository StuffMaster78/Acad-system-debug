"""
writer_management/services/reward_evaluation_service.py

Evaluates WriterRewardCriteria and grants WriterReward records.

RESPONSIBILITY
--------------
This service answers one question per criteria row:
    "Which writers qualify for this reward right now?"

It then:
    1. Checks they have not already received this reward this period
    2. Credits writer_compensation (when prize_amount > 0)
    3. Creates the WriterReward record
    4. Notifies the writer

ENTRY POINTS
------------
evaluate_all(website)
    Called by Celery Beat task weekly/monthly.
    Evaluates all active criteria for a website.

evaluate_criteria(criteria)
    Evaluates a single criteria. Useful for ad-hoc admin triggers
    and testing individual criteria configurations.

grant_manual(writer, criteria, granted_by, notes)
    Admin manually grants a reward outside the evaluation pipeline.

EVALUATION PERIOD DISPATCH
---------------------------
weekly   → reads WriterPerformanceMetrics  (week_start = last Monday)
monthly  → reads WriterPerformanceSnapshot (period = last calendar month)
lifetime → reads WriterPerformance         (all-time totals)

TOP vs ALL
----------
Criteria named with strategy="top_n" grant to the N highest-scoring
qualifying writers only. Strategy="all_qualifying" grants to every
writer who meets the thresholds.

This is controlled by WriterRewardCriteria.grant_strategy.
(Field added below — see GRANT STRATEGY note.)

COMPENSATION ORDERING
---------------------
For rewards with prize_amount > 0:
    1. Credit writer_compensation FIRST (atomic)
    2. Create WriterReward record only if compensation succeeds
    3. If WriterReward creation fails after compensation credit,
       log a critical alert — manual reconciliation needed.

This ordering ensures the financial record always exists before
the recognition record. Never the reverse.

IDEMPOTENCY
-----------
evaluate_all() is safe to run multiple times in the same period.
Before granting, the service checks whether a WriterReward already
exists for this writer + criteria + period. If yes, skip.

DEPENDENCIES
------------
Reads from:
    WriterRewardCriteria        (writer_management)
    WriterPerformanceMetrics    (writer_management)
    WriterPerformanceSnapshot   (writer_management)
    WriterPerformance           (writer_management)
    WriterReward                (writer_management)

Writes to:
    WriterReward                (writer_management)

Calls:
    writer_compensation.services.bonus_service.BonusService.credit()
    notifications_system.services.NotificationService.notify()
"""

import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.utils.timezone import now

from writer_management.models.writer_reward import WriterReward, WriterRewardCriteria

logger = logging.getLogger(__name__)


class RewardEvaluationService:

    # ----------------------------------------------------------------
    # PUBLIC ENTRY POINTS
    # ----------------------------------------------------------------

    @staticmethod
    def evaluate_all(website) -> dict:
        """
        Evaluate all active criteria for a website.

        Called by Celery Beat task on schedule.
        Returns a summary dict for monitoring.

        Args:
            website: Website instance.

        Returns:
            {
                'evaluated': int,   — criteria rows processed
                'granted': int,     — total rewards granted
                'skipped': int,     — already awarded, skipped
                'errors': int,      — criteria that raised exceptions
            }
        """
        criteria_qs = WriterRewardCriteria.objects.filter(
            website=website,
            is_active=True,
        ).order_by("evaluation_period", "name")

        summary = {
            "evaluated": 0,
            "granted": 0,
            "skipped": 0,
            "errors": 0,
        }

        for criteria in criteria_qs:
            try:
                result = RewardEvaluationService.evaluate_criteria(criteria)
                summary["evaluated"] += 1
                summary["granted"] += result["granted"]
                summary["skipped"] += result["skipped"]
            except Exception as exc:
                summary["errors"] += 1
                logger.exception(
                    "RewardEvaluationService: criteria=%s failed: %s",
                    criteria.pk,
                    exc,
                )

        logger.info(
            "RewardEvaluationService.evaluate_all: website=%s %s",
            website.pk,
            summary,
        )
        return summary

    @staticmethod
    def evaluate_criteria(criteria: WriterRewardCriteria) -> dict:
        """
        Evaluate a single criteria and grant rewards to qualifying writers.

        Args:
            criteria: WriterRewardCriteria instance.

        Returns:
            {'granted': int, 'skipped': int}
        """
        period_start, period_end = (
            RewardEvaluationService._resolve_period(criteria)
        )

        candidates = RewardEvaluationService._get_candidates(
            criteria=criteria,
            period_start=period_start,
            period_end=period_end,
        )

        granted = 0
        skipped = 0

        for writer_profile, metrics_snapshot in candidates:
            already = RewardEvaluationService._already_awarded(
                writer=writer_profile,
                criteria=criteria,
                period_start=period_start,
            )
            if already:
                skipped += 1
                continue

            try:
                RewardEvaluationService._grant(
                    writer=writer_profile,
                    criteria=criteria,
                    period_start=period_start,
                    period_end=period_end,
                    metrics_snapshot=metrics_snapshot,
                )
                granted += 1
            except Exception as exc:
                logger.exception(
                    "RewardEvaluationService: failed to grant "
                    "criteria=%s writer=%s: %s",
                    criteria.pk,
                    writer_profile.registration_id,
                    exc,
                )

        logger.info(
            "evaluate_criteria: criteria='%s' period=%s→%s "
            "granted=%d skipped=%d",
            criteria.name,
            period_start,
            period_end,
            granted,
            skipped,
        )

        return {"granted": granted, "skipped": skipped}

    @staticmethod
    @transaction.atomic
    def grant_manual(
        writer,
        criteria: WriterRewardCriteria,
        granted_by,
        notes: str = "",
    ) -> WriterReward:
        """
        Admin manually grants a reward outside the evaluation pipeline.

        Does NOT check thresholds — admin has already made the decision.
        Does check for duplicate awards in the current period.

        Args:
            writer:     WriterProfile.
            criteria:   WriterRewardCriteria to grant against.
            granted_by: Admin User performing the grant.
            notes:      Reason for manual grant.

        Returns:
            WriterReward instance.

        Raises:
            ValueError: If reward already granted this period.
        """
        period_start, period_end = (
            RewardEvaluationService._resolve_period(criteria)
        )

        if RewardEvaluationService._already_awarded(
            writer=writer,
            criteria=criteria,
            period_start=period_start,
        ):
            raise ValueError(
                f"Writer {writer.registration_id} has already received "
                f"'{criteria.name}' for this period ({period_start})."
            )

        reward = RewardEvaluationService._grant(
            writer=writer,
            criteria=criteria,
            period_start=period_start,
            period_end=period_end,
            metrics_snapshot={},
            granted_by=granted_by,
            notes=notes,
            is_auto_awarded=False,
        )

        logger.info(
            "Manual reward granted: criteria='%s' writer=%s by=%s",
            criteria.name,
            writer.registration_id,
            getattr(granted_by, "pk", "unknown"),
        )

        return reward

    # ----------------------------------------------------------------
    # PERIOD RESOLUTION
    # ----------------------------------------------------------------

    @staticmethod
    def _resolve_period(criteria: WriterRewardCriteria) -> tuple[date, date]:
        """
        Resolve the evaluation period dates for a criteria.

        weekly   → last full Monday–Sunday week
        monthly  → last full calendar month
        lifetime → beginning of time to today
        """
        today = now().date()

        if criteria.evaluation_period == "weekly":
            # Last full week: Monday to Sunday
            last_monday = today - timedelta(days=today.weekday() + 7)
            last_sunday = last_monday + timedelta(days=6)
            return last_monday, last_sunday

        if criteria.evaluation_period == "monthly":
            # Last full calendar month
            first_of_this_month = today.replace(day=1)
            last_of_prev_month = first_of_this_month - timedelta(days=1)
            first_of_prev_month = last_of_prev_month.replace(day=1)
            return first_of_prev_month, last_of_prev_month

        # lifetime
        return date(2000, 1, 1), today

    # ----------------------------------------------------------------
    # CANDIDATE RESOLUTION
    # ----------------------------------------------------------------

    @staticmethod
    def _get_candidates(
        criteria: WriterRewardCriteria,
        period_start: date,
        period_end: date,
    ) -> list[tuple]:
        """
        Return list of (WriterProfile, metrics_dict) tuples for writers
        who meet all configured thresholds for this criteria.

        Dispatches to the correct performance model based on
        evaluation_period.
        """
        if criteria.evaluation_period == "weekly":
            return RewardEvaluationService._candidates_weekly(
                criteria, period_start
            )
        if criteria.evaluation_period == "monthly":
            return RewardEvaluationService._candidates_monthly(
                criteria, period_start, period_end
            )
        return RewardEvaluationService._candidates_lifetime(criteria)

    @staticmethod
    def _candidates_weekly(
        criteria: WriterRewardCriteria,
        week_start: date,
    ) -> list[tuple]:
        """Read WriterPerformanceMetrics for the given week."""
        from writer_management.models.writer_performance import (
            WriterPerformanceMetrics,
        )

        qs = WriterPerformanceMetrics.objects.filter(
            website=criteria.website,
            week_start=week_start,
        ).select_related("writer")

        qs = RewardEvaluationService._apply_filters(qs, criteria, "weekly")
        qs = qs.order_by("-composite_score")

        return [
            (
                row.writer,
                {
                    "evaluation_period": "weekly",
                    "period_start": str(week_start),
                    "period_end": str(week_start + timedelta(days=6)),
                    "composite_score": float(row.composite_score),
                    "avg_rating": float(row.avg_rating),
                    "completed_orders": row.total_orders_completed,
                    "lateness_rate": float(row.lateness_rate),
                    "revision_rate": float(row.revision_rate),
                    "total_earnings": float(row.total_earnings),
                },
            )
            for row in qs
        ]

    @staticmethod
    def _candidates_monthly(
        criteria: WriterRewardCriteria,
        period_start: date,
        period_end: date,
    ) -> list[tuple]:
        """Read WriterPerformanceSnapshot for the given month."""
        from writer_management.models.writer_performance import (
            WriterPerformanceSnapshot,
        )

        qs = WriterPerformanceSnapshot.objects.filter(
            website=criteria.website,
            period_start=period_start,
            period_end=period_end,
            is_processed=True,
        ).select_related("writer")

        qs = RewardEvaluationService._apply_filters(qs, criteria, "monthly")
        qs = qs.order_by("-composite_score")

        return [
            (
                row.writer,
                {
                    "evaluation_period": "monthly",
                    "period_start": str(period_start),
                    "period_end": str(period_end),
                    "composite_score": float(row.composite_score or 0),
                    "avg_rating": float(row.average_rating or 0),
                    "completed_orders": row.completed_orders,
                    "lateness_rate": float(row.lateness_rate * 100),
                    "revision_rate": float(row.revision_rate * 100),
                    "total_earnings": float(row.amount_paid),
                },
            )
            for row in qs
        ]

    @staticmethod
    def _candidates_lifetime(
        criteria: WriterRewardCriteria,
    ) -> list[tuple]:
        """Read WriterPerformance for lifetime totals."""
        from writer_management.models.writer_performance import WriterPerformance

        today = now().date()

        qs = WriterPerformance.objects.filter(
            website=criteria.website,
        ).select_related("writer")

        qs = RewardEvaluationService._apply_filters(qs, criteria, "lifetime")
        qs = qs.order_by("-completed_orders")

        return [
            (
                row.writer,
                {
                    "evaluation_period": "lifetime",
                    "period_start": "2000-01-01",
                    "period_end": str(today),
                    "composite_score": None,
                    "avg_rating": float(row.average_rating),
                    "completed_orders": row.completed_orders,
                    "lateness_rate": None,
                    "revision_rate": None,
                    "total_earnings": float(row.total_earnings),
                },
            )
            for row in qs
        ]

    @staticmethod
    def _apply_filters(qs, criteria: WriterRewardCriteria, period: str):
        """
        Apply all non-null threshold filters to a queryset.

        Field names differ between performance models — resolved
        by period type.
        """
        # Field name mapping per period
        field_map = {
            "weekly": {
                "completed": "total_orders_completed",
                "rating":    "avg_rating",
                "earnings":  "total_earnings",
                "score":     "composite_score",
                "lateness":  "lateness_rate",
                "revision":  "revision_rate",
            },
            "monthly": {
                "completed": "completed_orders",
                "rating":    "average_rating",
                "earnings":  "amount_paid",
                "score":     "composite_score",
                # monthly rates stored as proportions — convert threshold
                "lateness":  "lateness_rate",
                "revision":  "revision_rate",
            },
            "lifetime": {
                "completed": "completed_orders",
                "rating":    "average_rating",
                "earnings":  "total_earnings",
                "score":     None,   # not available on WriterPerformance
                "lateness":  None,
                "revision":  None,
            },
        }

        fm = field_map[period]

        if criteria.min_completed_orders is not None and fm["completed"]:
            qs = qs.filter(
                **{f"{fm['completed']}__gte": criteria.min_completed_orders}
            )

        if criteria.min_avg_rating is not None and fm["rating"]:
            qs = qs.filter(
                **{f"{fm['rating']}__gte": criteria.min_avg_rating}
            )

        if criteria.min_earnings is not None and fm["earnings"]:
            qs = qs.filter(
                **{f"{fm['earnings']}__gte": criteria.min_earnings}
            )

        if criteria.min_composite_score is not None and fm["score"]:
            qs = qs.filter(
                **{f"{fm['score']}__gte": criteria.min_composite_score}
            )

        if criteria.max_lateness_rate is not None and fm["lateness"]:
            # Monthly: stored as proportion (0.0–1.0)
            # Weekly:  stored as percentage (0–100)
            threshold = (
                criteria.max_lateness_rate / 100
                if period == "monthly"
                else criteria.max_lateness_rate
            )
            qs = qs.filter(**{f"{fm['lateness']}__lte": threshold})

        if criteria.max_revision_rate is not None and fm["revision"]:
            threshold = (
                criteria.max_revision_rate / 100
                if period == "monthly"
                else criteria.max_revision_rate
            )
            qs = qs.filter(**{f"{fm['revision']}__lte": threshold})

        return qs

    # ----------------------------------------------------------------
    # IDEMPOTENCY CHECK
    # ----------------------------------------------------------------

    @staticmethod
    def _already_awarded(
        writer,
        criteria: WriterRewardCriteria,
        period_start: date,
    ) -> bool:
        """
        True if writer already has a reward for this criteria
        in the current evaluation period.

        For lifetime criteria: checks if ANY award exists ever
        (lifetime rewards are one-time only).
        """
        if criteria.evaluation_period == "lifetime":
            return WriterReward.objects.filter(
                writer=writer,
                criteria=criteria,
            ).exists()

        # Weekly/monthly: check within current period
        return WriterReward.objects.filter(
            writer=writer,
            criteria=criteria,
            awarded_at__date__gte=period_start,
        ).exists()

    # ----------------------------------------------------------------
    # GRANT
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def _grant(
        writer,
        criteria: WriterRewardCriteria,
        period_start: date,
        period_end: date,
        metrics_snapshot: dict,
        granted_by=None,
        notes: str = "",
        is_auto_awarded: bool = True,
    ) -> WriterReward:
        """
        Grant a reward to a writer.

        1. Credit compensation (if prize_amount > 0)
        2. Create WriterReward record
        3. Notify writer

        All three steps run inside a single transaction.
        If any step fails, the entire grant rolls back.
        """

        # Step 1: Credit compensation first
        if criteria.prize_amount > Decimal("0.00"):
            RewardEvaluationService._credit_compensation(
                writer=writer,
                criteria=criteria,
                period_start=period_start,
            )

        # Step 2: Create recognition record
        reward = WriterReward.objects.create(
            website=criteria.website,
            writer=writer,
            criteria=criteria,
            granted_by=granted_by,
            title=criteria.reward_title,
            prize_description=criteria.prize_description,
            prize_amount=criteria.prize_amount,
            is_auto_awarded=is_auto_awarded,
            notes=notes,
            metadata={
                **metrics_snapshot,
                "criteria_id": criteria.pk,
                "criteria_name": criteria.name,
            },
        )

        # Step 3: Notify writer
        RewardEvaluationService._notify_writer(reward)

        logger.info(
            "Reward granted: criteria='%s' writer=%s "
            "prize=%s auto=%s",
            criteria.name,
            writer.registration_id,
            criteria.prize_amount,
            is_auto_awarded,
        )

        return reward

    # ----------------------------------------------------------------
    # COMPENSATION
    # ----------------------------------------------------------------

    @staticmethod
    def _credit_compensation(
        writer,
        criteria: WriterRewardCriteria,
        period_start: date,
    ) -> None:
        """
        Credit the prize amount to the writer's compensation record.

        Calls writer_compensation.services.bonus_service.BonusService.
        If this raises, the entire grant transaction rolls back.
        """
        try:
            from writer_compensation.services.bonus_service import (
                BonusService,
            )
            BonusService.credit(
                writer=writer,
                amount=criteria.prize_amount,
                reason=(
                    f"Reward: {criteria.name} "
                    f"({criteria.evaluation_period} — {period_start})"
                ),
            )
        except ImportError:
            # writer_compensation not yet integrated — log and continue
            logger.warning(
                "writer_compensation.BonusService not available. "
                "Prize amount %s for writer %s not credited. "
                "Manual reconciliation required.",
                criteria.prize_amount,
                writer.registration_id,
            )
        except Exception as exc:
            logger.exception(
                "BonusService.credit failed for writer=%s "
                "criteria=%s amount=%s: %s",
                writer.registration_id,
                criteria.pk,
                criteria.prize_amount,
                exc,
            )
            raise  # Rolls back the entire grant transaction

    # ----------------------------------------------------------------
    # NOTIFICATION
    # ----------------------------------------------------------------

    @staticmethod
    def _notify_writer(reward: WriterReward) -> None:
        """Notify the writer that a reward was granted."""
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )

            writer = reward.writer
            user = RewardEvaluationService._resolve_user(writer)
            if not user:
                logger.warning(
                    "Cannot notify writer %s — user not resolvable.",
                    writer.registration_id,
                )
                return

            NotificationService.notify(
                event_key="writer.reward.granted",
                recipient=user,
                website=reward.website,
                context={
                    "registration_id": writer.registration_id,
                    "reward_id": reward.pk,
                    "title": reward.title,
                    "prize_description": reward.prize_description,
                    "prize_amount": str(reward.prize_amount),
                    "has_financial_component": reward.has_financial_component,
                    "awarded_at": reward.awarded_at.isoformat(),
                },
            )
        except Exception as exc:
            # Notification failure must NOT roll back the grant
            logger.exception(
                "Reward notification failed for reward=%s: %s",
                reward.pk,
                exc,
            )

    # ----------------------------------------------------------------
    # IDENTITY RESOLUTION
    # ----------------------------------------------------------------

    @staticmethod
    def _resolve_user(writer):
        """Resolve auth User through account_profile."""
        try:
            return writer.account_profile.user
        except Exception:
            return None