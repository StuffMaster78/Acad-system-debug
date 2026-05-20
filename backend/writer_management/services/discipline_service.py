"""
writer_management/services/discipline_service.py

All discipline mutations go through this service.
Nothing else writes to discipline models directly.

OPERATIONS
----------
issue_strike()          → WriterStrike
suspend()               → WriterSuspension
lift_suspension()       → updates WriterSuspension
blacklist()             → WriterBlacklist
lift_blacklist()        → updates WriterBlacklist
place_on_probation()    → WriterProbation
end_probation()         → updates WriterProbation
apply_penalty()         → WriterPenalty
expire_ended_actions()  → called by Celery task — clears timed-out
                          suspensions and probations

AFTER EVERY MUTATION
--------------------
DisciplineService calls WriterStatusService.recompute(writer)
which rebuilds WriterDisciplineState from the source records.
WriterStatusService then calls WriterCapacity update to sync
can_take_orders.

This keeps the cache consistent without signals or triggers.

IDENTITY RESOLUTION
-------------------
WriterProfile has no .user or .website.
All resolution goes through _resolve_website() and _resolve_user().

NOTIFICATION
------------
DisciplineNotificationService handles all notifications.
This service calls it — it does not import NotificationService directly.
"""

import logging
from datetime import timedelta

from django.db import transaction
from django.utils.timezone import now

from writer_management.models import (
    WriterBlacklist,
    WriterBlacklistHistory,
    WriterDisciplineConfig,
    WriterPenalty,
    WriterProbation,
    WriterStrike,
    WriterSuspension,
    WriterSuspensionHistory,
    WriterProfile,
)
from writer_management.exceptions import (
    WriterBlacklistedError,
    WriterSuspendedError,
)

logger = logging.getLogger(__name__)


class DisciplineService:

    # ----------------------------------------------------------------
    # STRIKES
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def issue_strike(
        writer: WriterProfile,
        reason: str,
        issued_by=None,
    ) -> WriterStrike:
        """
        Issue a disciplinary strike to a writer.

        After creation, evaluates whether strike thresholds trigger
        automatic suspension or blacklisting.

        Args:
            writer:    WriterProfile receiving the strike.
            reason:    Why the strike is being issued.
            issued_by: Admin User. None = system-triggered.

        Returns:
            WriterStrike instance.
        """
        website = DisciplineService._resolve_website(writer)

        strike = WriterStrike.objects.create(
            website=website,
            writer=writer,
            reason=reason,
            issued_by=issued_by,
        )

        logger.info(
            "WriterStrike issued: writer=%s strike=%s reason=%r",
            writer.registration_id,
            strike.pk,
            reason[:80],
        )

        DisciplineService._recompute_state(writer)
        DisciplineService._evaluate_strike_thresholds(
            writer=writer,
            website=website,
            issued_by=issued_by,
        )
        DisciplineService._notify(
            "writer.discipline.strike_issued",
            writer=writer,
            context={
                "strike_id": strike.pk,
                "reason": reason,
            },
            triggered_by=issued_by,
        )

        return strike

    @staticmethod
    def _evaluate_strike_thresholds(writer, website, issued_by) -> None:
        """
        Check if strike count has crossed auto-suspension or
        auto-blacklist thresholds. Trigger accordingly.
        """
        try:
            config = WriterDisciplineConfig.objects.get(website=website)
        except WriterDisciplineConfig.DoesNotExist:
            logger.warning(
                "No WriterDisciplineConfig for website %s — "
                "skipping threshold evaluation.",
                website.pk,
            )
            return

        lifetime_strikes = WriterStrike.objects.filter(
            writer=writer
        ).count()

        # Blacklist threshold (lifetime strikes — irreversible)
        if (
            config.auto_blacklist_on_strikes > 0 and
            lifetime_strikes >= config.auto_blacklist_on_strikes and
            not WriterBlacklist.objects.filter(
                writer=writer, is_active=True
            ).exists()
        ):
            logger.warning(
                "Auto-blacklist threshold reached: writer=%s strikes=%d",
                writer.registration_id,
                lifetime_strikes,
            )
            DisciplineService.blacklist(
                writer=writer,
                reason=(
                    f"Auto-blacklisted: reached {lifetime_strikes} "
                    f"lifetime strikes (threshold: "
                    f"{config.auto_blacklist_on_strikes})."
                ),
                auto_triggered=True,
            )
            return

        # Suspension threshold (lifetime strikes — use same count)
        if (
            config.auto_suspend_on_strikes > 0 and
            lifetime_strikes >= config.auto_suspend_on_strikes and
            not WriterSuspension.objects.filter(
                writer=writer, is_active=True
            ).exists()
        ):
            logger.warning(
                "Auto-suspension threshold reached: writer=%s strikes=%d",
                writer.registration_id,
                lifetime_strikes,
            )
            DisciplineService.suspend(
                writer=writer,
                reason=(
                    f"Auto-suspended: reached {lifetime_strikes} "
                    f"strikes (threshold: "
                    f"{config.auto_suspend_on_strikes})."
                ),
                duration_days=config.auto_suspend_days,
                auto_triggered=True,
            )

    # ----------------------------------------------------------------
    # SUSPENSION
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def suspend(
        writer: WriterProfile,
        reason: str,
        duration_days: int | None = None,
        suspended_by=None,
        auto_triggered: bool = False,
    ) -> WriterSuspension:
        """
        Suspend a writer.

        Raises WriterBlacklistedError if writer is already blacklisted —
        blacklist supersedes suspension, do not create redundant record.
        Raises WriterSuspendedError if already suspended.

        Args:
            writer:         WriterProfile to suspend.
            reason:         Why the writer is being suspended.
            duration_days:  Days until suspension ends. None = indefinite.
            suspended_by:   Admin User. None = auto-triggered.
            auto_triggered: True when triggered by threshold logic.

        Returns:
            WriterSuspension instance.
        """
        website = DisciplineService._resolve_website(writer)

        # Guard: blacklist supersedes suspension
        if WriterBlacklist.objects.filter(
            writer=writer, is_active=True
        ).exists():
            raise WriterBlacklistedError(
                f"Writer {writer.registration_id} is blacklisted. "
                "Cannot create a suspension on a blacklisted writer."
            )

        # Guard: only one active suspension at a time
        if WriterSuspension.objects.filter(
            writer=writer, is_active=True
        ).exists():
            raise WriterSuspendedError(
                f"Writer {writer.registration_id} is already suspended. "
                "Lift the current suspension before creating a new one."
            )

        end_date = (
            now() + timedelta(days=duration_days)
            if duration_days
            else None
        )

        suspension = WriterSuspension.objects.create(
            website=website,
            writer=writer,
            reason=reason,
            auto_triggered=auto_triggered,
            suspended_by=suspended_by,
            end_date=end_date,
        )

        WriterSuspensionHistory.objects.create(
            suspension=suspension,
            changed_by=suspended_by,
            change_type="auto_triggered" if auto_triggered else "created",
            notes=reason,
        )

        logger.info(
            "WriterSuspension created: writer=%s suspension=%s "
            "auto=%s days=%s",
            writer.registration_id,
            suspension.pk,
            auto_triggered,
            duration_days,
        )

        DisciplineService._recompute_state(writer)
        DisciplineService._notify(
            "writer.discipline.suspended",
            writer=writer,
            context={
                "suspension_id": suspension.pk,
                "reason": reason,
                "end_date": end_date.isoformat() if end_date else None,
                "auto_triggered": auto_triggered,
            },
            triggered_by=suspended_by,
        )

        return suspension

    @staticmethod
    @transaction.atomic
    def lift_suspension(
        writer: WriterProfile,
        lifted_by=None,
        reason: str = "",
    ) -> WriterSuspension:
        """
        Lift the active suspension for a writer.

        Raises WriterSuspendedError if no active suspension exists.

        Args:
            writer:    WriterProfile to unsuspend.
            lifted_by: Admin User performing the lift.
            reason:    Optional reason for lifting early.

        Returns:
            Updated WriterSuspension instance.
        """
        try:
            suspension = WriterSuspension.objects.get(
                writer=writer, is_active=True
            )
        except WriterSuspension.DoesNotExist:
            raise WriterSuspendedError(
                f"Writer {writer.registration_id} has no active suspension."
            )

        suspension.is_active = False
        suspension.lifted_at = now()
        suspension.lifted_by = lifted_by
        suspension.lift_reason = reason
        suspension.save(update_fields=[
            "is_active", "lifted_at", "lifted_by", "lift_reason"
        ])

        WriterSuspensionHistory.objects.create(
            suspension=suspension,
            changed_by=lifted_by,
            change_type="lifted",
            notes=reason,
        )

        logger.info(
            "WriterSuspension lifted: writer=%s suspension=%s by=%s",
            writer.registration_id,
            suspension.pk,
            getattr(lifted_by, "pk", "system"),
        )

        DisciplineService._recompute_state(writer)
        DisciplineService._notify(
            "writer.discipline.suspension_lifted",
            writer=writer,
            context={"suspension_id": suspension.pk, "reason": reason},
            triggered_by=lifted_by,
        )

        return suspension

    # ----------------------------------------------------------------
    # BLACKLIST
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def blacklist(
        writer: WriterProfile,
        reason: str,
        blacklisted_by=None,
        auto_triggered: bool = False,
    ) -> WriterBlacklist:
        """
        Blacklist a writer.

        If the writer is currently suspended, the suspension is
        automatically lifted first — blacklist supersedes it.

        Args:
            writer:         WriterProfile to blacklist.
            reason:         Why the writer is being blacklisted.
            blacklisted_by: Admin User. None = auto-triggered.
            auto_triggered: True when triggered by threshold logic.

        Returns:
            WriterBlacklist instance.
        """
        website = DisciplineService._resolve_website(writer)

        # Guard: already blacklisted
        if WriterBlacklist.objects.filter(
            writer=writer, is_active=True
        ).exists():
            logger.warning(
                "blacklist() called on already-blacklisted writer %s.",
                writer.registration_id,
            )
            return WriterBlacklist.objects.get(
                writer=writer, is_active=True
            )

        # Lift any active suspension — blacklist supersedes it
        try:
            DisciplineService.lift_suspension(
                writer=writer,
                lifted_by=blacklisted_by,
                reason="Lifted — blacklist applied.",
            )
        except WriterSuspendedError:
            pass  # No active suspension — that's fine

        entry = WriterBlacklist.objects.create(
            website=website,
            writer=writer,
            reason=reason,
            auto_triggered=auto_triggered,
            blacklisted_by=blacklisted_by,
        )

        WriterBlacklistHistory.objects.create(
            blacklist=entry,
            changed_by=blacklisted_by,
            change_type="auto_triggered" if auto_triggered else "created",
            notes=reason,
        )

        logger.warning(
            "WriterBlacklist created: writer=%s blacklist=%s auto=%s",
            writer.registration_id,
            entry.pk,
            auto_triggered,
        )

        DisciplineService._recompute_state(writer)
        DisciplineService._notify(
            "writer.discipline.blacklisted",
            writer=writer,
            context={
                "blacklist_id": entry.pk,
                "reason": reason,
                "auto_triggered": auto_triggered,
            },
            triggered_by=blacklisted_by,
        )

        return entry

    @staticmethod
    @transaction.atomic
    def lift_blacklist(
        writer: WriterProfile,
        lifted_by=None,
        reason: str = "",
    ) -> WriterBlacklist:
        """
        Lift the active blacklist for a writer.

        This is a significant action. Log carefully.

        Args:
            writer:    WriterProfile to un-blacklist.
            lifted_by: Admin User performing the lift.
            reason:    Why the blacklist is being lifted.

        Returns:
            Updated WriterBlacklist instance.
        """
        try:
            entry = WriterBlacklist.objects.get(
                writer=writer, is_active=True
            )
        except WriterBlacklist.DoesNotExist:
            raise WriterBlacklistedError(
                f"Writer {writer.registration_id} has no active blacklist."
            )

        entry.is_active = False
        entry.lifted_at = now()
        entry.lifted_by = lifted_by
        entry.lift_reason = reason
        entry.save(update_fields=[
            "is_active", "lifted_at", "lifted_by", "lift_reason"
        ])

        WriterBlacklistHistory.objects.create(
            blacklist=entry,
            changed_by=lifted_by,
            change_type="lifted",
            notes=reason,
        )

        logger.warning(
            "WriterBlacklist LIFTED: writer=%s blacklist=%s by=%s "
            "reason=%r",
            writer.registration_id,
            entry.pk,
            getattr(lifted_by, "pk", "system"),
            reason[:80],
        )

        DisciplineService._recompute_state(writer)
        DisciplineService._notify(
            "writer.discipline.blacklist_lifted",
            writer=writer,
            context={"blacklist_id": entry.pk, "reason": reason},
            triggered_by=lifted_by,
        )

        return entry

    # ----------------------------------------------------------------
    # PROBATION
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def place_on_probation(
        writer: WriterProfile,
        reason: str,
        end_date=None,
        duration_days: int = 30,
        placed_by=None,
        auto_triggered: bool = False,
    ) -> WriterProbation:
        """
        Place a writer on probation.

        Args:
            writer:         WriterProfile.
            reason:         Why.
            end_date:       Explicit end datetime. Overrides duration_days.
            duration_days:  Days of probation if end_date not given.
            placed_by:      Admin User. None = auto.
            auto_triggered: True when triggered by warning threshold.

        Returns:
            WriterProbation instance.
        """
        website = DisciplineService._resolve_website(writer)

        if WriterProbation.objects.filter(
            writer=writer, is_active=True
        ).exists():
            logger.info(
                "Writer %s already on probation — skipping.",
                writer.registration_id,
            )
            return WriterProbation.objects.get(
                writer=writer, is_active=True
            )

        resolved_end = end_date or (
            now() + timedelta(days=duration_days)
        )

        probation = WriterProbation.objects.create(
            website=website,
            writer=writer,
            reason=reason,
            auto_triggered=auto_triggered,
            placed_by=placed_by,
            end_date=resolved_end,
        )

        logger.info(
            "WriterProbation created: writer=%s probation=%s "
            "auto=%s ends=%s",
            writer.registration_id,
            probation.pk,
            auto_triggered,
            resolved_end.date(),
        )

        DisciplineService._recompute_state(writer)
        DisciplineService._notify(
            "writer.discipline.probation_placed",
            writer=writer,
            context={
                "probation_id": probation.pk,
                "reason": reason,
                "end_date": resolved_end.isoformat(),
            },
            triggered_by=placed_by,
        )

        return probation

    @staticmethod
    @transaction.atomic
    def end_probation(
        writer: WriterProfile,
        ended_by=None,
        reason: str = "",
    ) -> WriterProbation:
        """End the active probation for a writer."""
        try:
            probation = WriterProbation.objects.get(
                writer=writer, is_active=True
            )
        except WriterProbation.DoesNotExist:
            raise ValueError(
                f"Writer {writer.registration_id} has no active probation."
            )

        probation.is_active = False
        probation.ended_at = now()
        probation.save(update_fields=["is_active", "ended_at"])

        logger.info(
            "WriterProbation ended: writer=%s probation=%s",
            writer.registration_id,
            probation.pk,
        )

        DisciplineService._recompute_state(writer)

        return probation

    # ----------------------------------------------------------------
    # PENALTY
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def apply_penalty(
        writer: WriterProfile,
        reason: str,
        amount: "Decimal",
        order=None,
        applied_by=None,
        notes: str = "",
    ) -> WriterPenalty:
        """
        Record a financial penalty for a writer.

        This creates the disciplinary record only.
        The actual earnings deduction is executed by writer_compensation.

        Args:
            writer:     WriterProfile.
            reason:     PenaltyReason choice value.
            amount:     Decimal amount to deduct.
            order:      orders.Order if penalty relates to a specific order.
            applied_by: Admin User.
            notes:      Additional context.

        Returns:
            WriterPenalty instance.
        """
        website = DisciplineService._resolve_website(writer)

        penalty = WriterPenalty.objects.create(
            website=website,
            writer=writer,
            order=order,
            reason=reason,
            amount_deducted=amount,
            applied_by=applied_by,
            notes=notes,
        )

        logger.info(
            "WriterPenalty applied: writer=%s penalty=%s "
            "amount=%s reason=%s",
            writer.registration_id,
            penalty.pk,
            amount,
            reason,
        )

        DisciplineService._notify(
            "writer.discipline.penalty_applied",
            writer=writer,
            context={
                "penalty_id": penalty.pk,
                "reason": reason,
                "amount": str(amount),
                "order_id": getattr(order, "pk", None),
            },
            triggered_by=applied_by,
        )

        return penalty

    # ----------------------------------------------------------------
    # EXPIRY TASK ENTRY POINT
    # Called by Celery Beat task — not by request-response path.
    # ----------------------------------------------------------------

    @staticmethod
    def expire_ended_actions() -> dict:
        """
        Expire suspensions and probations whose end dates have passed.

        Called by the daily discipline expiry Celery task.
        Returns counts for monitoring.
        """
        n = now()
        expired_suspensions = 0
        expired_probations = 0

        # Expire timed-out suspensions
        due_suspensions = WriterSuspension.objects.filter(
            is_active=True,
            end_date__lte=n,
        ).select_related("writer")

        for suspension in due_suspensions:
            try:
                DisciplineService.lift_suspension(
                    writer=suspension.writer,
                    reason="Auto-expired: suspension period ended.",
                )
                expired_suspensions += 1
            except Exception as exc:
                logger.exception(
                    "Failed to auto-expire suspension %s: %s",
                    suspension.pk,
                    exc,
                )

        # Expire timed-out probations
        due_probations = WriterProbation.objects.filter(
            is_active=True,
            end_date__lte=n,
        ).select_related("writer")

        for probation in due_probations:
            try:
                DisciplineService.end_probation(
                    writer=probation.writer,
                    reason="Auto-expired: probation period ended.",
                )
                expired_probations += 1
            except Exception as exc:
                logger.exception(
                    "Failed to auto-expire probation %s: %s",
                    probation.pk,
                    exc,
                )

        logger.info(
            "expire_ended_actions: suspensions=%d probations=%d",
            expired_suspensions,
            expired_probations,
        )

        return {
            "expired_suspensions": expired_suspensions,
            "expired_probations": expired_probations,
        }

    # ----------------------------------------------------------------
    # PRIVATE HELPERS
    # ----------------------------------------------------------------

    @staticmethod
    def _recompute_state(writer: WriterProfile) -> None:
        """
        Rebuild WriterDisciplineState from source records.
        Called after every discipline mutation.
        """
        try:
            from writer_management.services.status_service import (
                WriterStatusService,
            )
            WriterStatusService.recompute(writer)
        except Exception as exc:
            logger.exception(
                "Failed to recompute discipline state for writer %s: %s",
                writer.registration_id,
                exc,
            )

    @staticmethod
    def _notify(event_key: str, writer: WriterProfile,
                context: dict, triggered_by=None) -> None:
        """Delegate notification to DisciplineNotificationService."""
        try:
            from writer_management.services.discipline_notification_service import (
                DisciplineNotificationService,
            )
            DisciplineNotificationService.notify(
                event_key=event_key,
                writer=writer,
                context=context,
                triggered_by=triggered_by,
            )
        except Exception as exc:
            logger.exception(
                "Discipline notification failed [%s] writer=%s: %s",
                event_key,
                writer.registration_id,
                exc,
            )

    @staticmethod
    def _resolve_website(writer: WriterProfile):
        """Resolve website through writer_level or account_profile."""
        try:
            if writer.writer_level_id:
                return writer.writer_level.website
        except Exception:
            pass
        try:
            return writer.account_profile.website
        except Exception:
            pass
        raise ValueError(
            f"Cannot resolve website for writer {writer.registration_id}."
        )
