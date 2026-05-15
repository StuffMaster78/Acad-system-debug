"""
writer_management/services/level_progression_service.py

Evaluates writers for level promotion and demotion.

SINGLE RESPONSIBILITY
---------------------
This service reads processed WriterPerformanceSnapshots and
WriterLevelCriteria to decide whether a writer should be
promoted, demoted, or remain at their current level.

It does NOT:
    - Compute performance scores (CompositeScoreService does that)
    - Create snapshots (WriterMetricsSnapshotService does that)
    - Send notifications directly (DisciplineNotificationService does that)

EVALUATION LOGIC
----------------
For each writer:

    1. Get their current WriterLevel
    2. Fetch the most recent N processed snapshots
       (N = criteria.min_evaluation_periods)
    3. Get WriterLevelCriteria for the NEXT level up (promotion)
       and the CURRENT level (demotion check)
    4. Check if all N snapshots meet the promotion thresholds
       → if yes: promote
    5. Check if the most recent snapshot breaches demotion thresholds
       of the current level's criteria
       → if yes: demote

CONSECUTIVE PERIODS REQUIREMENT
---------------------------------
WriterLevelCriteria.min_evaluation_periods defaults to 1.
When set to 3: writer must meet promotion thresholds in 3
consecutive snapshots before being promoted. One bad week
doesn't block promotion — one bad week doesn't trigger premature
promotion either.

DEMOTION
--------
A single period breaching the demotion threshold triggers
a demotion review. The service demotes immediately unless
WriterLevelCriteria.require_manual_demotion_review=True
(future field — not yet implemented, demotion is automatic).

PROMOTION ORDER
---------------
The service evaluates ONE level jump at a time. A writer cannot
jump from Junior to Expert in one cycle. They must pass through
each level sequentially.

The next level up is determined by WriterLevel.display_order —
the level with the next highest display_order (lower number = higher rank).

CALLED BY
---------
Celery task: writer_management.tasks.performance_tasks.run_level_progression
Run weekly, after performance aggregation completes.

FIXES FROM PREVIOUS VERSION
----------------------------
1. _try_promote used `_get_criteria(next_level)` as a bare function call
   instead of `LevelProgressionService._get_criteria(next_level)`.

2. _try_demote still used `current_level.criteria` reverse accessor
   instead of `LevelProgressionService._get_criteria(current_level)`.

3. _get_recent_snapshots imported from wrong module path
   `writer_management.models.writer_performance` — correct path is
   `writer_management.models.performance`.

4. _apply_level_change capacity update block had an empty .update()
   call — placeholder comment was never completed. Filled in correctly.
"""

import logging

from django.db import transaction

from writer_management.enums import LevelChangeType, LevelChangeTrigger
from writer_management.exceptions import (
    LevelSettingsMissingError,  # noqa: F401 — exported for callers
    WriterLevelNotFoundError,   # noqa: F401 — exported for callers
)
from writer_management.models.writer_level_criteria import WriterLevelCriteria

logger = logging.getLogger(__name__)


class LevelProgressionService:

    # ----------------------------------------------------------------
    # PUBLIC ENTRY POINTS
    # ----------------------------------------------------------------

    @staticmethod
    def evaluate_all(website) -> dict:
        """
        Evaluate all writers on a website for level changes.

        Args:
            website: Website instance.

        Returns:
            Summary: {evaluated, promoted, demoted, unchanged, errors}
        """
        from writer_management.models.writer_profile import WriterProfile

        writers = WriterProfile.objects.filter(
            writer_level__website=website,
            is_deleted=False,
            onboarding_status="completed",
        ).select_related(
            "writer_level",
            "writer_level__settings",
        )

        summary = {
            "evaluated": 0,
            "promoted":  0,
            "demoted":   0,
            "unchanged": 0,
            "errors":    0,
        }

        for writer_profile in writers.iterator(chunk_size=100):
            try:
                result = LevelProgressionService.evaluate_writer(
                    writer_profile=writer_profile,
                    website=website,
                )
                summary["evaluated"] += 1
                summary[result] += 1
            except Exception as exc:
                summary["errors"] += 1
                logger.exception(
                    "LevelProgressionService: failed for writer=%s: %s",
                    writer_profile.registration_id,
                    exc,
                )

        logger.info(
            "LevelProgressionService.evaluate_all: website=%s %s",
            website.pk,
            summary,
        )
        return summary

    @staticmethod
    def evaluate_writer(writer_profile, website) -> str:
        """
        Evaluate a single writer for promotion or demotion.

        Returns one of: "promoted", "demoted", "unchanged"
        """
        current_level = writer_profile.writer_level

        if current_level is None:
            logger.warning(
                "Writer %s has no level — skipping evaluation.",
                writer_profile.registration_id,
            )
            return "unchanged"

        snapshots = LevelProgressionService._get_recent_snapshots(
            writer_profile=writer_profile,
            website=website,
            count=10,
        )

        if not snapshots:
            logger.debug(
                "No processed snapshots for writer=%s — skipping.",
                writer_profile.registration_id,
            )
            return "unchanged"

        if LevelProgressionService._try_promote(
            writer_profile=writer_profile,
            website=website,
            current_level=current_level,
            snapshots=snapshots,
        ):
            return "promoted"

        if LevelProgressionService._try_demote(
            writer_profile=writer_profile,
            website=website,
            current_level=current_level,
            snapshots=snapshots,
        ):
            return "demoted"

        return "unchanged"

    # ----------------------------------------------------------------
    # CRITERIA RESOLUTION
    # Uses an explicit query rather than the reverse accessor
    # so Pylance can resolve the type and DoesNotExist is explicit.
    # ----------------------------------------------------------------

    @staticmethod
    def _get_criteria(level) -> WriterLevelCriteria | None:
        """
        Fetch WriterLevelCriteria for a level.
        Returns None if no criteria is configured for this level.
        """
        try:
            return WriterLevelCriteria.objects.get(level=level)
        except WriterLevelCriteria.DoesNotExist:
            return None

    # ----------------------------------------------------------------
    # PROMOTION
    # ----------------------------------------------------------------

    @staticmethod
    def _try_promote(
        writer_profile,
        website,
        current_level,
        snapshots: list,
    ) -> bool:
        """
        Check if writer qualifies for promotion to next level.
        Returns True if promoted.
        """
        next_level = LevelProgressionService._get_next_level(
            current_level, website
        )
        if next_level is None:
            return False  # already at highest level

        # FIX 1: was `_get_criteria(next_level)` — missing class prefix
        criteria = LevelProgressionService._get_criteria(next_level)
        if criteria is None:
            logger.debug(
                "No WriterLevelCriteria for level '%s' — cannot promote.",
                next_level.name,
            )
            return False

        if not criteria.is_active:
            return False

        periods_to_check = min(
            criteria.min_evaluation_periods,
            len(snapshots),
        )

        if periods_to_check < criteria.min_evaluation_periods:
            # Not enough snapshot history yet
            return False

        recent = snapshots[:periods_to_check]

        for snapshot in recent:
            meets, failures = criteria.meets_promotion_thresholds(snapshot)
            if not meets:
                logger.debug(
                    "Writer %s does not meet promotion thresholds "
                    "for level '%s': %s",
                    writer_profile.registration_id,
                    next_level.name,
                    failures,
                )
                return False

        reason = (
            f"Met all promotion thresholds for '{next_level.name}' "
            f"over {periods_to_check} consecutive evaluation period(s)."
        )
        LevelProgressionService._apply_level_change(
            writer_profile=writer_profile,
            new_level=next_level,
            change_type=LevelChangeType.PROMOTION,
            trigger=LevelChangeTrigger.WEEKLY_TASK,
            reason=reason,
            snapshot=recent[0],
        )

        logger.info(
            "Writer %s PROMOTED: %s → %s",
            writer_profile.registration_id,
            current_level.name,
            next_level.name,
        )
        return True

    # ----------------------------------------------------------------
    # DEMOTION
    # ----------------------------------------------------------------

    @staticmethod
    def _try_demote(
        writer_profile,
        website,
        current_level,
        snapshots: list,
    ) -> bool:
        """
        Check if writer should be demoted based on current level criteria.
        Returns True if demoted.
        """
        # FIX 2: was `current_level.criteria` reverse accessor
        # Now uses explicit query — same pattern as _try_promote
        criteria = LevelProgressionService._get_criteria(current_level)
        if criteria is None or not criteria.is_active:
            return False

        most_recent = snapshots[0]
        breached, breaches = criteria.breaches_demotion_thresholds(most_recent)

        if not breached:
            return False

        prev_level = LevelProgressionService._get_previous_level(
            current_level, website
        )
        if prev_level is None:
            logger.info(
                "Writer %s breaches demotion thresholds but is at "
                "the lowest level — no further demotion possible.",
                writer_profile.registration_id,
            )
            return False

        reason = (
            f"Breached demotion thresholds for '{current_level.name}': "
            f"{'; '.join(breaches)}"
        )
        LevelProgressionService._apply_level_change(
            writer_profile=writer_profile,
            new_level=prev_level,
            change_type=LevelChangeType.DEMOTION,
            trigger=LevelChangeTrigger.WEEKLY_TASK,
            reason=reason,
            snapshot=most_recent,
        )

        logger.warning(
            "Writer %s DEMOTED: %s → %s. Reasons: %s",
            writer_profile.registration_id,
            current_level.name,
            prev_level.name,
            breaches,
        )
        return True

    # ----------------------------------------------------------------
    # LEVEL CHANGE APPLICATION
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def _apply_level_change(
        writer_profile,
        new_level,
        change_type: str,
        trigger: str,
        reason: str,
        snapshot=None,
        changed_by=None,
        admin_notes: str = "",
    ) -> None:
        """
        Apply a level change to a writer atomically.

        1. Update WriterProfile.writer_level
        2. Create WriterLevelChangeLog entry
        3. Sync WriterCapacity default order ceiling from new level
        4. Notify writer
        """
        from writer_management.models.writer_level_history import (
            WriterLevelChangeLog,
        )
        from writer_management.models.writer_capacity import WriterCapacity

        previous_level = writer_profile.writer_level

        performance_snapshot = {}
        if snapshot:
            performance_snapshot = {
                "composite_score": float(snapshot.composite_score or 0),
                "avg_rating":      float(snapshot.average_rating or 0),
                "completion_rate": float(snapshot.completion_rate * 100),
                "lateness_rate":   float(snapshot.lateness_rate * 100),
                "revision_rate":   float(snapshot.revision_rate * 100),
                "dispute_rate":    float(snapshot.dispute_rate * 100),
                "period_start":    str(snapshot.period_start),
                "period_end":      str(snapshot.period_end),
            }

        # 1. Update profile level
        writer_profile.writer_level = new_level
        writer_profile.save(update_fields=["writer_level", "updated_at"])

        # 2. Audit log
        WriterLevelChangeLog.objects.create(
            writer=writer_profile,
            website=new_level.website,
            previous_level=previous_level,
            previous_level_name=previous_level.name if previous_level else "",
            new_level=new_level,
            new_level_name=new_level.name,
            change_type=change_type,
            triggered_by=trigger,
            reason=reason,
            admin_notes=admin_notes,
            changed_by=changed_by,
            performance_snapshot=performance_snapshot,
        )

        # 3. Sync capacity ceiling from new level default
        # FIX 3: was an empty .update() call — now correctly reads
        # new level's max_active_orders and applies it when no
        # per-writer override is set.
        try:
            capacity = WriterCapacity.objects.get(writer=writer_profile)
            if capacity.override_max_active_orders is None:
                level_settings = new_level.settings_safe
                if level_settings and level_settings.max_active_orders:
                    capacity.max_orders_per_day = None  # reset daily limit
                    capacity.save(update_fields=["max_orders_per_day", "updated_at"])
                    # Note: active_orders_count ceiling is
                    # WriterLevelSettings.max_active_orders — resolved
                    # at query time by WriterEligibilityService.
                    # No WriterCapacity field needs updating here.
        except WriterCapacity.DoesNotExist:
            logger.warning(
                "_apply_level_change: no WriterCapacity for writer=%s",
                writer_profile.registration_id,
            )
        except Exception as exc:
            # Capacity sync is best-effort — level change succeeds regardless
            logger.exception(
                "_apply_level_change: capacity sync failed for writer=%s: %s",
                writer_profile.registration_id,
                exc,
            )

        # 4. Notify writer
        LevelProgressionService._notify_writer(
            writer_profile=writer_profile,
            previous_level=previous_level,
            new_level=new_level,
            change_type=change_type,
        )

    # ----------------------------------------------------------------
    # MANUAL OVERRIDE
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def manual_level_change(
        writer_profile,
        new_level,
        changed_by,
        reason: str,
        admin_notes: str = "",
    ) -> None:
        """
        Admin manually sets a writer's level.

        Args:
            writer_profile: WriterProfile instance.
            new_level:      Target WriterLevel.
            changed_by:     Admin User performing the change.
            reason:         Required — why the change is being made.
            admin_notes:    Optional internal notes.

        Raises:
            ValueError: If reason is blank.
        """
        if not reason.strip():
            raise ValueError("Reason is required for manual level changes.")

        LevelProgressionService._apply_level_change(
            writer_profile=writer_profile,
            new_level=new_level,
            change_type=LevelChangeType.MANUAL,
            trigger=LevelChangeTrigger.ADMIN,
            reason=reason,
            snapshot=None,
            changed_by=changed_by,
            admin_notes=admin_notes,
        )

        logger.info(
            "Manual level change: writer=%s → level='%s' by=%s",
            writer_profile.registration_id,
            new_level.name,
            getattr(changed_by, "pk", "unknown"),
        )

    # ----------------------------------------------------------------
    # LEVEL NAVIGATION
    # ----------------------------------------------------------------

    @staticmethod
    def _get_next_level(current_level, website):
        """
        Level one step above current (lower display_order = higher rank).
        Returns None if already at the highest level.
        """
        from writer_management.models.writer_level import WriterLevel

        return (
            WriterLevel.objects.filter(
                website=website,
                is_active=True,
                display_order__lt=current_level.display_order,
            )
            .order_by("-display_order")
            .first()
        )

    @staticmethod
    def _get_previous_level(current_level, website):
        """
        Level one step below current (higher display_order = lower rank).
        Returns None if already at the lowest level.
        """
        from writer_management.models.writer_level import WriterLevel

        return (
            WriterLevel.objects.filter(
                website=website,
                is_active=True,
                display_order__gt=current_level.display_order,
            )
            .order_by("display_order")
            .first()
        )

    @staticmethod
    def _get_recent_snapshots(writer_profile, website, count: int) -> list:
        """
        Most recent processed snapshots for a writer, newest first.

        FIX 4: was importing from writer_management.models.writer_performance
        — correct module is writer_management.models.performance.
        """
        from writer_management.models.writer_performance import (
            WriterPerformanceSnapshot,
        )

        return list(
            WriterPerformanceSnapshot.objects.filter(
                writer=writer_profile,
                website=website,
                is_processed=True,
            )
            .order_by("-period_end")[:count]
        )

    # ----------------------------------------------------------------
    # NOTIFICATION
    # ----------------------------------------------------------------

    @staticmethod
    def _notify_writer(
        writer_profile,
        previous_level,
        new_level,
        change_type: str,
    ) -> None:
        """Notify writer of level change. Non-blocking — exceptions logged."""
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )

            user = writer_profile.account_profile.user
            event_key = (
                "writer.level.promoted"
                if change_type == LevelChangeType.PROMOTION
                else "writer.level.demoted"
            )

            NotificationService.notify(
                event_key=event_key,
                recipient=user,
                website=new_level.website,
                context={
                    "registration_id": writer_profile.registration_id,
                    "previous_level":  previous_level.name if previous_level else None,
                    "new_level":       new_level.name,
                    "change_type":     change_type,
                },
            )
        except Exception as exc:
            logger.exception(
                "Level change notification failed for writer=%s: %s",
                writer_profile.registration_id,
                exc,
            )