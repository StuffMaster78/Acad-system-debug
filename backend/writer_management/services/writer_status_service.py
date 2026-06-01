"""
Rebuilds WriterDisciplineState from source discipline records.

SINGLE RESPONSIBILITY
---------------------
This service answers one question:
    "Given all the discipline source records for this writer,
     what is their current derived state?"

It reads from:
    WriterStrike (lifetime and active strike counts)
    WriterWarning (active and lifetime warning counts)
    WriterSuspension (is_suspended, suspension_ends_at)
    WriterBlacklist (is_blacklisted)
    WriterProbation (is_on_probation, probation_ends_at)

It writes to:
    WriterDisciplineState (the cache)
    WriterCapacity.can_take_orders (synced from discipline state)

WHEN IS IT CALLED
-----------------
After every mutation in DisciplineService:
    issue_strike()
    suspend() / lift_suspension()
    blacklist() / lift_blacklist()
    place_on_probation() / end_probation()
    void_strike() / void_warning()

Also called by the daily expiry Celery task after
DisciplineService.expire_ended_actions() runs.

ATOMICITY
---------
recompute() runs inside a transaction.atomic() block.
If WriterDisciplineState update fails, the calling discipline
mutation rolls back too — ensuring cache and source records
never diverge due to a partial write.
"""

import logging

from django.db import models, transaction
from django.utils.timezone import now

from writer_management.models.writer_discipline_state import WriterDisciplineState

logger = logging.getLogger(__name__)


class WriterStatusService:

    @staticmethod
    @transaction.atomic
    def recompute(writer_profile) -> WriterDisciplineState:
        """
        Rebuild WriterDisciplineState from source discipline records.

        Called after every discipline mutation.
        Uses select_for_update on the state row to prevent
        concurrent recompute races.

        Args:
            writer_profile: WriterProfile instance.

        Returns:
            Updated WriterDisciplineState instance.
        """
        from writer_management.models.writer_discipline import (
            WriterBlacklist,
            WriterProbation,
            WriterSuspension,
        )
        from writer_management.models.writer_strike import WriterStrike
        from writer_management.models.writer_warning import WriterWarning
        from writer_management.models.writer_capacity import WriterCapacity

        n = now()

        # Lock the state row for this recompute
        state, _ = WriterDisciplineState.objects.select_for_update(
            nowait=False
        ).get_or_create(writer=writer_profile)

        # ----------------------------------------------------------------
        # STRIKES
        # Active = not voided (strikes never expire)
        # Lifetime = all strikes ever including voided
        # ----------------------------------------------------------------

        active_strike_count = WriterStrike.objects.filter(
            writer=writer_profile,
            is_voided=False,
        ).count()

        lifetime_strike_count = WriterStrike.objects.filter(
            writer=writer_profile,
        ).count()

        # ----------------------------------------------------------------
        # WARNINGS
        # Active = is_active=True, is_voided=False, not expired
        # Lifetime = all warnings ever
        # ----------------------------------------------------------------

        active_warning_count = WriterWarning.objects.filter(
            writer=writer_profile,
            is_active=True,
            is_voided=False,
        ).filter(
            models.Q(expires_at__isnull=True) |
            models.Q(expires_at__gt=n)
        ).count()

        lifetime_warning_count = WriterWarning.objects.filter(
            writer=writer_profile,
        ).count()

        # ----------------------------------------------------------------
        # SUSPENSION
        # ----------------------------------------------------------------

        try:
            suspension = WriterSuspension.objects.get(
                writer=writer_profile,
                is_active=True,
            )
            is_suspended = True
            suspension_ends_at = suspension.end_date
        except WriterSuspension.DoesNotExist:
            is_suspended = False
            suspension_ends_at = None

        # ----------------------------------------------------------------
        # BLACKLIST
        # ----------------------------------------------------------------

        is_blacklisted = WriterBlacklist.objects.filter(
            writer=writer_profile,
            is_active=True,
        ).exists()

        # ----------------------------------------------------------------
        # PROBATION
        # ----------------------------------------------------------------

        try:
            probation = WriterProbation.objects.get(
                writer=writer_profile,
                is_active=True,
            )
            is_on_probation = True
            probation_ends_at = probation.end_date
        except WriterProbation.DoesNotExist:
            is_on_probation = False
            probation_ends_at = None

        # ----------------------------------------------------------------
        # LAST DISCIPLINE EVENT
        # Most recent event across strikes and warnings
        # ----------------------------------------------------------------

        last_strike = WriterStrike.objects.filter(
            writer=writer_profile
        ).order_by("-issued_at").values_list("issued_at", flat=True).first()

        last_warning = WriterWarning.objects.filter(
            writer=writer_profile
        ).order_by("-created_at").values_list("created_at", flat=True).first()

        last_event_at = None
        if last_strike and last_warning:
            last_event_at = max(last_strike, last_warning)
        elif last_strike:
            last_event_at = last_strike
        elif last_warning:
            last_event_at = last_warning

        # ----------------------------------------------------------------
        # UPDATE STATE
        # ----------------------------------------------------------------

        state.is_suspended = is_suspended
        state.is_blacklisted = is_blacklisted
        state.is_on_probation = is_on_probation
        state.active_strike_count = active_strike_count
        state.lifetime_strike_count = lifetime_strike_count
        state.active_warning_count = active_warning_count
        state.lifetime_warning_count = lifetime_warning_count
        state.suspension_ends_at = suspension_ends_at
        state.probation_ends_at = probation_ends_at
        state.last_discipline_event_at = last_event_at

        state.save(update_fields=[
            "is_suspended",
            "is_blacklisted",
            "is_on_probation",
            "active_strike_count",
            "lifetime_strike_count",
            "active_warning_count",
            "lifetime_warning_count",
            "suspension_ends_at",
            "probation_ends_at",
            "last_discipline_event_at",
            "updated_at",
        ])

        # ----------------------------------------------------------------
        # SYNC WriterCapacity.can_take_orders
        # Suspended or blacklisted writers cannot take orders.
        # Probation alone does not block order taking.
        # ----------------------------------------------------------------

        restricted = is_suspended or is_blacklisted

        WriterCapacity.objects.filter(
            writer=writer_profile,
        ).update(can_take_orders=not restricted)

        logger.info(
            "WriterDisciplineState recomputed: writer=%s "
            "suspended=%s blacklisted=%s probation=%s "
            "active_strikes=%d active_warnings=%d",
            writer_profile.registration_id,
            is_suspended,
            is_blacklisted,
            is_on_probation,
            active_strike_count,
            active_warning_count,
        )

        return state

    @staticmethod
    def get_state(writer_profile) -> WriterDisciplineState:
        """
        Retrieve the current discipline state for a writer.
        Creates a clean default state if none exists.
        """
        state, created = WriterDisciplineState.objects.get_or_create(
            writer=writer_profile,
        )
        if created:
            logger.warning(
                "WriterDisciplineState created on-demand for writer=%s. "
                "Should have been bootstrapped by signal.",
                writer_profile.registration_id,
            )
        return state

    @staticmethod
    def is_restricted(writer_profile) -> bool:
        """
        Fast check: is this writer currently suspended or blacklisted?
        Reads the cache — no source record queries.
        """
        try:
            state = writer_profile.discipline_state
            return state.is_suspended or state.is_blacklisted
        except WriterDisciplineState.DoesNotExist:
            return False